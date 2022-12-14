import pandas as pd
from image_responses import ImageResponses


class FormExtractor:
    """
    Form Structure:
    Datetime | Email | Question1 | Question2
    """
    RESPONSES_INDEX_LIST = None

    def __init__(self, form_path, responses_index_list: list = []) -> None:
        self.form = pd.read_excel(form_path)

        # Testing python attr level access
        responses_size = len(responses_index_list)
        if responses_size > 0 and responses_size <= len(self.form):
            FormExtractor.RESPONSES_INDEX_LIST = responses_index_list
        else:
            self.RESPONSES_INDEX_LIST = range(len(self.form))

        # remove ununcessary fields
        self.form = self.form.drop(axis='columns', labels=[
                                   'Carimbo de data/hora', 'Endereço de e-mail'])

    def get_image_responses(self, image: dict) -> list[ImageResponses]:
        form_responses = self.extract_form_image_responses(image['id'])

        responses_list = []
        for index, response in form_responses.iterrows():
            formated_response = self.format_response_as_list(response)
            image_responses = ImageResponses(
                index, image, formated_response[0], formated_response[1])
            responses_list.append(image_responses)

        return responses_list

    def extract_form_image_responses(self, image_index: int) -> pd.DataFrame:
        """
        extracts the dataframe columns referring to the answers 
        of questions 1 and 2 to the image
        """
        form_indexes = image_index * 2, image_index * 2+1

        responses = self.form.iloc[
            self.RESPONSES_INDEX_LIST, [
                form_indexes[0], form_indexes[1]]
        ]

        return responses

    def format_response_as_list(self, response: pd.Series) -> list:
        formated_responses = []
        for question_response in response:
            question_words = question_response.lower().split(',')
            formated_responses.append(
                [formated_word.strip() for formated_word in question_words]
            )

        return formated_responses

    @staticmethod
    def get_n_responses(form_path) -> None:
        form = pd.read_excel(form_path)

        if FormExtractor.RESPONSES_INDEX_LIST:
            return len(FormExtractor.RESPONSES_INDEX_LIST)

        return len(form)
