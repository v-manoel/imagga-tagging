from tags_generator import RekognitionApiHandler
from constants import AnalyserConfigs, FormConfigs
from form_extractor import FormExtractor
from utils import Utils
import numpy as np
import matplotlib.pyplot as plt
from unidecode import unidecode


class Analyser:

    def __init__(self, responses_index_list: list = []) -> None:
        self.apihandler = RekognitionApiHandler()
        self.extractor = FormExtractor(
            FormConfigs.FORM_FILE_PATH, responses_index_list
        )

    def set_image_data(self, image: dict) -> None:
        tags_api = self.apihandler.get_image_tags(
            image['url'], AnalyserConfigs.GENERATED_TAGS_LIMIT
        )

        self.image = image
        self.generated_tags = [tag['name'] for tag in tags_api]

        responses = self.extractor.get_image_responses(image)
        grouped_responses = self.group_image_responses(responses)
        self.n_responses = len(responses)
        self.q1_reponses = grouped_responses[0]
        self.q2_reponses = grouped_responses[1]

    def group_image_responses(self, image_responses: list) -> list:
        q1_grouped_responses = []
        q2_grouped_responses = []

        for response in image_responses:
            q1_grouped_responses.extend(response.manual_tags)

            format_tags = [unidecode(tag) for tag in response.checked_tags]
            q2_grouped_responses.extend(format_tags)

        return q1_grouped_responses, q2_grouped_responses

    @staticmethod
    def stack_bar_chart(xvalues: list, yvalues: list[dict], filename: str = "compare_chart") -> None:
        fig = plt.figure(facecolor="white")
        fig.set_size_inches(18.5, 10.5)

        ax = fig.add_subplot(1, 1, 1)
        bar_width = 0.5
        bar_l = np.arange(1, len(xvalues)+1)

        tick_pos = [i + (bar_width / 2) for i in bar_l]

        ax.grid()
        ax1 = ax.bar(
            bar_l, yvalues[0]['value'], width=bar_width,
            label=yvalues[0]['label'], color="green", zorder=3
        )
        ax2 = ax.bar(
            bar_l, yvalues[1]['value'], width=bar_width,
            label=yvalues[1]['label'], color="blue", zorder=2,
            bottom=np.array(yvalues[0]['value'])
        )
        ax3 = ax.bar(
            bar_l, yvalues[2]['value'], width=bar_width,
            label=yvalues[2]['label'], color="red", zorder=1,
            bottom=np.array(yvalues[0]['value']) +
            np.array(yvalues[1]['value'])
        )

        ax.set_ylabel("Count", fontsize=10)
        ax.set_xlabel("images", fontsize=10)
        ax.legend(loc="best")

        ylim = (FormExtractor.get_n_responses(FormConfigs.FORM_FILE_PATH) * FormConfigs.MIN_HUMAN_TAGS) + \
            AnalyserConfigs.GENERATED_TAGS_LIMIT

        ax.set_ylim([0, ylim])

        plt.xticks(tick_pos, xvalues, fontsize=10)
        plt.yticks(fontsize=10)

        for r1, r2, r3 in zip(ax1, ax2, ax3):
            h1 = r1.get_height()
            h2 = r2.get_height()
            h3 = r3.get_height()
            plt.text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1,
                     ha="center", va="bottom", color="white", fontsize=10, fontweight="bold")
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2,
                     ha="center", va="bottom", color="white", fontsize=10, fontweight="bold")
            plt.text(r3.get_x() + r3.get_width() / 2., h1 + h2 + h3 / 2., "%d" % h3,
                     ha="center", va="bottom", color="white", fontsize=10, fontweight="bold")

        plt.show()

        fig.savefig(f'{filename}.png')

    def analyse_q1_responses(self, normalized: bool = False) -> dict:
        generated_tags_set = set(self.generated_tags)
        q1_responses_set = set(self.q1_reponses)

        if normalized:
            q1_responses_set = Utils.normalize_words_set(
                generated_tags_set,
                q1_responses_set
            )

        intersec = generated_tags_set & q1_responses_set
        manual_only = q1_responses_set - generated_tags_set
        auto_only = generated_tags_set - q1_responses_set

        return {'intersec': intersec, 'manual only': manual_only, 'auto only': auto_only}

    @staticmethod
    def bar_chart(xvalues: list, yvalues: dict, filename: str = "acceptance_chart") -> None:
        fig = plt.figure(facecolor="white")
        fig.set_size_inches(18.5, 10.5)

        ax = fig.add_subplot(1, 1, 1)
        bar_width = 0.5
        bar_l = np.arange(1, len(xvalues)+1)

        tick_pos = [i + (bar_width / 2) for i in bar_l]

        ax.grid(zorder=1)
        ax1 = ax.bar(bar_l, yvalues['value'], width=bar_width,
                     label=yvalues['label'], color="green", zorder=2)
        ax.set_ylabel("Count", fontsize=10)
        ax.set_xlabel("images", fontsize=10)
        ax.legend(loc="best")

        plt.xticks(tick_pos, xvalues, fontsize=10)
        plt.yticks(fontsize=10)
        ax.bar_label(ax1, padding=3)

        plt.show()
        fig.savefig(f'{filename}.png')

    def analyse_q2_responses(self):
        generated_tags_set = set(self.generated_tags)

        tag_occurences = {}
        counter = []
        for tag in generated_tags_set:
            ocurrence = self.q2_reponses.count(unidecode(tag))
            tag_occurences[tag] = ocurrence
            counter.append(ocurrence/self.n_responses)

        acceptance = sum(counter)/AnalyserConfigs.GENERATED_TAGS_LIMIT

        return (tag_occurences, round(acceptance, 2))

    def output_q1_result(self, normalized: bool = False) -> dict:
        q1_analysis = self.analyse_q1_responses(normalized)

        return {
            'image': self.image,
            'common tags': {
                'lenght': len(q1_analysis['intersec']),
                'tags': list(q1_analysis['intersec'])
            },
            'generated tags': {
                'lenght': len(q1_analysis['auto only']),
                'tags': list(q1_analysis['auto only'])
            },
            'collected tags': {
                'lenght': len(q1_analysis['manual only']),
                'tags': list(q1_analysis['manual only'])
            },
        }

    def output_q2_result(self) -> dict:
        q2_analysis = self.analyse_q2_responses()

        return {
            'image': self.image,
            'responses': self.n_responses,
            'tags occurrence': q2_analysis[0],
            'acceptance': q2_analysis[1],
        }
