import logging

from dotenv import load_dotenv
from app.modules.fakenodo.repositories import DepositionRepo
from app.modules.dataset.models import DataSet
from app.modules.featuremodel.models import FeatureModel

from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)

load_dotenv()


class FakenodoService(BaseService):
    def __init__(self):
        self.deposition_repository = DepositionRepo()

    def create_new_deposition(self, dataset: DataSet) -> dict:
        """
        Create a new deposition in Fakenodo

        Args:
            dataset (Dataset): The dataset contain ing the necessary metadata

        Returns:
            dict: JSON format with the details of the deposition
        """

        logger.info("Dataset sending to Fakenodo")
        logger.info(f"Publication type: {dataset.ds_meta_data.publication_type.value}")

        metadataJSON = {
            "title": dataset.ds_meta_data.title,
            "upload_type": "dataset" if dataset.ds_meta_data.publication_type.value == "none" else "publication",
            "publication_type": (
                dataset.ds_meta_data.publication_type.value
                if dataset.ds_meta_data.publication_type.value != "none"
                else None
            ),
            "description": dataset.ds_meta_data.description,
            "creators": [
                {
                    "name": author.name,
                    **({"affiliation": author.affiliation} if author.affiliation else {}),
                    **({"orcid": author.orcid} if author.orcid else {}),
                }
                for author in dataset.ds_meta_data.authors
            ],
            "keywords": (
                ["uvlhub"] if not dataset.ds_meta_data.tags else dataset.ds_meta_data.tags.split(", ") + ["uvlhub"]
            ),
            "access_right": "open",
            "license": "CC-BY-4.0",
        }

        try:
            deposition = self.deposition_repository.create_new_deposition(metadata=metadataJSON)

            return {
                "id": deposition.id,
                "metadata": metadataJSON,
                "message": "Deposition succesfully created in Fakenodo"
            }
        except Exception as error400:
            raise Exception(f"Failed to create deposition in Fakenodo with error: {str(error400)}")

    def upload_file(self, dataset: DataSet, deposition_id: int, feature_model: FeatureModel, user=None):
        """
        Upload a file to a deposition in Fakenodo.

        Args:
            deposition_id (int): The ID of the deposition in Fakenodo.
            feature_model (FeatureModel): The FeatureModel object representing the feature model.
            user (FeatureModel): The User object representing the file owner.

        Returns:
            dict: The response in JSON format with the details of the uploaded file.
        """