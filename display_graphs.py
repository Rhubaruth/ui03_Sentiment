import numpy as np

BAR_WIDTH: float = 0.3

class graph_data:
    values: list
    label: str
    color: str
    alpha: float

    def __init__(self, values: list = None, label: str = '', color: str = 'b', alpha: float = 0.8):
        self.values = values
        self.label = label
        self.color = color
        self.alpha = alpha


def display_vertical(plot, verdict_labels,
                     green_data: graph_data, blue_data: graph_data):
    """ Creates a vertical bargraph with 2 columns on each label """

    n_groups = len(verdict_labels)
    index = np.arange(n_groups)

    plot.bar(index, green_data.values, BAR_WIDTH,
         alpha=0.8,
         color=green_data.color,
         label=green_data.label)
    plot.bar(index + BAR_WIDTH, blue_data.values, BAR_WIDTH,
         alpha=0.8,
         color=blue_data.color,
         label=blue_data.label)
    plot.xticks(index + BAR_WIDTH/2, verdict_labels)
    plot.legend()
    plot.tight_layout()

    # plt.bar(index, list(eval_verdicts['Correct']), 0.3,
    #      alpha=0.8,
    #      color='g',
    #      label='AI\'s agrees with User')
    # plt.bar(index + 0.3, list(eval_verdicts['Wrong']), 0.3,
    #      alpha=0.8,
    #      color='r',
    #      label='AI does not agree')
    # plt.xticks(index + 0.15, verdict_labels)
    # plt.legend()
    # plt.tight_layout()

# def display_horizontal(plot, horizontal_labels):
#     n_groups = len(horizontal_labels)
#     word_labels: list[str] = []
#     for idx, val in enumerate(all_counts.most_common(num_words)[::-1]):
#         word, count = val
#         plot.barh(idx, count, BAR_WIDTH,
#              alpha=0.8,
#              color='b')
#         word_labels.append(word)
#     plot.yticks(range(n_groups), word_labels)
#     plot.tight_layout()
