from app.modules.fakenodo.models import Deposition

from core.repositories.BaseRepository import BaseRepository

from app import db


class DepositionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Deposition)

    def createDeposition(self, metadata=None, doi=None):  # Damos un valor por defecto a ambos campos
        """
        Crea una nueva Deposition de Fakenodo

        Args:
            metadata (dict, optional): Json o Diccionario con metadata de la deposición
            doi (str, optional): El DOI de la deposición

        Returns:
            Deposition: La deposición creada
        """
        if metadata is None:
            metadata = {}

        # Usamos `meta_data` para coincidir con el modelo
        depo = Deposition(meta_data=metadata, doi=doi)
        db.session.add(depo)
        db.session.commit()

        return depo
