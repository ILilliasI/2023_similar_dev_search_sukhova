from collections import Counter, defaultdict
from typing import Any, Dict, List

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarDevelopersFinder:
    """
    Class that finds similar developers.
    """

    LANGUAGE_FIELD = "languages"
    VARIABLES_FIELD = "variables"

    SIMILAR_DEVELOPERS_NUMBER = 15

    @staticmethod
    def _get_developers_dataframe(developers_info: Dict[str, Any]) -> pd.DataFrame:
        """
        Get pandas dataframe from python dictionary.
        :param developers_info: Dict with information about developers.
        :return: Pandas dataframe with information about developers.
        """
        vectorizer = DictVectorizer(dtype=int, sparse=False)
        dev_matrix = vectorizer.fit_transform(developers_info.values())

        dev_df = pd.DataFrame(dev_matrix, columns=vectorizer.feature_names_, index=list(developers_info.keys()))
        dev_df.fillna(0, inplace=True)
        return dev_df

    def _get_developers_info_for_df(self, developers_info: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get processed dict with information about developers to create pandas dataframe.
        :param developers_info: Dict with information about developers.
        :return: Processed dict with information about developers.
        """
        developers_info_for_df = defaultdict(Counter)
        for dev_email, repos_info in developers_info.items():
            for repo_name, repo_info in repos_info.items():
                developers_info_for_df[dev_email] += Counter(
                    {**repo_info[self.VARIABLES_FIELD], **repo_info[self.LANGUAGE_FIELD]}
                )
        return developers_info_for_df

    def get_similar_developers(self, user_email: str, developers_info: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Get similar developers for given developer.
        :param user_email: Email of developer to find similar.
        :param developers_info: Dict with information about developers.
        :return: Similar developers emails with similarity scores.
        """
        developers_info_for_df = self._get_developers_info_for_df(developers_info)
        del developers_info

        developers_df = self._get_developers_dataframe(developers_info_for_df)
        del developers_info_for_df

        dev_similarity = cosine_similarity(
            developers_df[developers_df.index != user_email], developers_df[developers_df.index == user_email]
        ).reshape(-1)
        res_similarity = list(zip(developers_df[developers_df.index != user_email].index, dev_similarity))
        res_similarity_sorted = sorted(res_similarity, key=lambda res: res[1], reverse=True)

        return dict(res_similarity_sorted[: self.SIMILAR_DEVELOPERS_NUMBER])
