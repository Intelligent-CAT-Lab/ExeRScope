import os
import matplotlib.pyplot as plt
import numpy as np
from venny4py.venny4py import *
from venn import pseudovenn, venn
import json
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import pandas as pd

import seaborn as sns


def box_plot(all_data, labels, xlabel, ylabel, title):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4, 4))

    # generate some random test data
    # plot violin plot
    ax.boxplot(all_data)
    ax.set_title(title)

    ax.yaxis.grid(True)
    ax.set_xticks([y + 1 for y in range(len(all_data))],
                labels=labels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.savefig(f"/home/changshu/LLM_REASONING/analysis/figs/complexity/{title}.png" , bbox_inches='tight', dpi=500)
    plt.show()

def violin_box_plot(all_data, labels, xlabel, ylabel, title):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 3))

    # generate some random test data
    # plot violin plot
    ax.violinplot(all_data,
                    # showmeans=True,
                    showmedians=True,
                    )
    # ax.set_title(title)

    ax.yaxis.grid(True)
    ax.set_xticks([y + 1 for y in range(len(all_data))],
                labels=labels)
    # ax.set_xlabel(xlabel, fontsize=18)
    # yax = ax.get_yticks()
    # # yticks_label = [f"{num}" if i % 5 !=0 else '' for i,num in enumerate(yax)]
    # # print(yticks_label)
    # yticks_label = ['0', '10', '20', '30', '40', '50']
    # ax.set_yticks(yax, yticks_label)
    plt.yticks(np.arange(0, 100, 10), fontsize=20)
    ax.set_ylabel(ylabel, fontsize=30)
    plt.xticks(fontsize=20, rotation=-40)
    plt.ylim(0, 50)
    print(f"/home/changshu/LLM_REASONING/analysis/figs/synthesis/{title}_voilin.png")
    plt.savefig(f"/home/changshu/LLM_REASONING/analysis/figs/synthesis/{title}_voilin.png" , bbox_inches='tight', dpi=500)
    plt.show()

def venn_diagram(sets, savepath):
    pseudovenn(sets, legend_loc="upper right", hint_hidden=False)
    plt.savefig(savepath, bbox_inches='tight', dpi=500)

def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

# data = [np.random.normal(0, std, 100) for std in range(6, 10)]
# labels = ['x1', 'x2', 'x3', 'x4']
# labelx = 'Four separate samples'
# labely = "'Observed values'"
# print(data)
# violin_box_plot(data, labels, labelx, labely, "test")

# sets = {
#     'Set1': set(list("Harry Potter")),
#     'Set2': set(list("Hermione Granger")),
#     'Set3': set(list("Ron Weasley")),
#     'Set4': set(list("Severus Snape"))}
# savepath = "/home/changshu/LLM_REASONING/analysis/figs/venntest.png"
# venn_diagram(sets, savepath)




def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):

        def transform_path_non_affine(self, path):
            # Paths with non-unit interpolation steps correspond to gridlines,
            # in which case we force interpolation (to defeat PolarTransform's
            # autoconversion to circular arcs).
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):

        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def example_data():
    # The following data is from the Denver Aerosol Sources and Health study.
    # See doi:10.1016/j.atmosenv.2008.12.017
    #
    # The data are pollution source profile estimates for five modeled
    # pollution sources (e.g., cars, wood-burning, etc) that emit 7-9 chemical
    # species. The radar charts are experimented with here to see if we can
    # nicely visualize how the modeled source profiles change across four
    # scenarios:
    #  1) No gas-phase species present, just seven particulate counts on
    #     Sulfate
    #     Nitrate
    #     Elemental Carbon (EC)
    #     Organic Carbon fraction 1 (OC)
    #     Organic Carbon fraction 2 (OC2)
    #     Organic Carbon fraction 3 (OC3)
    #     Pyrolyzed Organic Carbon (OP)
    #  2)Inclusion of gas-phase specie carbon monoxide (CO)
    #  3)Inclusion of gas-phase specie ozone (O3).
    #  4)Inclusion of both gas-phase species is present...
    data = [
        ['Nested Loop', 'If', 'For', 'While', 'Try', 'Basic'],
        ('CodeNet(Python)', [
            [0.4551083591331269, 0.6875502008032128, 0.5435294117647059, 0.5714285714285714, 0.3333333333333333, 0.8333333333333334],
            [0.16408668730650156, 0.344578313253012, 0.21411764705882352, 0.23809523809523808, 0.0, 0.4839357429718876]
            ])
    ]
    return data


def star_plot(data, N, labels, title):
    
    theta = radar_factory(N, frame='polygon')
    # data = example_data()
    spoke_labels = data.pop(0)
    fig, ax = plt.subplots(figsize=(10, 10), nrows=1, ncols=1,
                            subplot_kw=dict(projection='radar'))
    
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    colors = ['b', 'r', 'g', 'm', 'black']
    # Plot the four cases from the example data on separate axes
    # for ax, (title, case_data) in zip(axs.flat, data):
    ax.set_rgrids([0.2, 0.4, 0.6, 0.8])
    # ax.set_title(ç, weight='bold', size=20, position=(0.5, 1.1),
    #                 horizontalalignment='center', verticalalignment='center')
    for d, color in zip(data[0][1], colors):
        ax.plot(theta, d, color=color, linewidth=10)
        ax.fill(theta, d, facecolor=color, alpha=0.25, label='_nolegend_')
    ax.set_varlabels(spoke_labels)
    ax.tick_params(labelsize=150, pad=0)
    # plt.xticks([])
    frame = plt.gca()
    frame.axes.yaxis.set_ticklabels([])
    # plt.yticks([])
    # plt.yticks([])
    # labels = ('GPT-4', 'MagicCoder')
    # add legend relative to top-left plot
    
    legend = ax.legend(labels, loc=(1, 1),
                              labelspacing=0.1, fontsize=30, ncols=1)
    # for line in legend.get_lines():
    #     line.set_linewidth(20)
    
    # fig.text(0.5, 0.965, '',
    #          horizontalalignment='center', color='black', weight='bold',
    #          size=15)

    plt.savefig(f"../Experiment_Results/figures/constructs/{title}_.png", bbox_inches='tight', dpi=500)


def violin_seaborn(df, x, y, hue, title):
    sns.set(rc={'figure.figsize':(12,5)})
    sns.set_theme(style="whitegrid")
    # df = sns.load_dataset("titanic")
    # print(df)
    ax = sns.violinplot(data=df, x=x, y=y, hue=hue, split=True, inner="quart")
    fig = ax.get_figure()
    plt.savefig(f"/home/changshu/LLM_REASONING/analysis/figs/complexity/{title}.pdf", bbox_inches='tight', dpi=500)

# star_plot()