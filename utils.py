from pysinonimos.sinonimos import Search
import json


class Utils:

    @staticmethod
    def substitute_synonyms(base_word: str, synonymos: str) -> str:
        glossary = Search(base_word).synonyms()

        if glossary != 404 and synonymos.lower() in glossary:
            return base_word

        return synonymos

    @staticmethod
    def normalize_words_set(base_list: set, synonymos_list: set) -> set:
        normalized_list = []

        for word in synonymos_list:
            normalized_word = word
            if word not in base_list:
                for base_word in base_list:
                    normalized_word = Utils.substitute_synonyms(
                        base_word, normalized_word)
            normalized_list.append(normalized_word)

        return set(normalized_list)

    @staticmethod
    def to_json_file(data, json_file: str):
        with open(f"{json_file}.json", "w") as outfile:
            json.dump(data, outfile, ensure_ascii=False)
