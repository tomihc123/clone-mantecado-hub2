from sqlalchemy import or_
from sqlalchemy.orm import aliased
from app import db
from app.modules.dataset.models import DSMetaData, DataSet, Author, PublicationType
from core.repositories.BaseRepository import BaseRepository


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter_datasets(self, query_string, sorting="newest", publication_type="any",uvl_min="",uvl_max=""):
        # Crear un alias para `ds_meta_data` para evitar conflictos de alias.
        ds_meta_data_alias = aliased(DSMetaData)
        author_meta_data_alias = aliased(DSMetaData)  # Nuevo alias para la segunda unión
        min_size_filter = None
        max_size_filter = None

        # Inicia la consulta, usando el alias en la unión
        query = db.session.query(DataSet).join(ds_meta_data_alias, DataSet.ds_meta_data)

        # Filtrar por tipo de publicación
        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break
            if matching_type is not None:
                query = query.filter(ds_meta_data_alias.publication_type == matching_type.name)

        # Procesar el filtro de `query_string`
        query_filter = query_string.strip()

        for filter_item in query_filter.split(';'):
            # Filtrar por etiquetas
            if filter_item.startswith('tags:'):
                tag_value = filter_item[5:].strip()
                query = query.filter(ds_meta_data_alias.tags.ilike(f'%{tag_value}%'))
                
            # Filtrar por el número máximo de modelos que tiene el dataset
            elif filter_item.startswith('models_max:'):
                models_max_value = filter_item[11:].strip()
                uvl_max = models_max_value

            # Filtrar por el número mínimo de modelos que tiene el dataset
            elif filter_item.startswith('models_min:'):
                models_min_value = filter_item[11:].strip()
                uvl_min = models_min_value

            # Filtrar por tamaño mínimo del dataset
            elif filter_item.startswith('min_size:'):
                try:
                    min_size_filter = int(filter_item[9:].strip())
                except ValueError:
                    min_size_filter = None

            # Filtrar por tamaño máximo del dataset
            elif filter_item.startswith('max_size:'):
                try:
                    max_size_filter = int(filter_item[9:].strip())
                except ValueError:
                    max_size_filter = None

            # Filtrar por autor
            elif filter_item.startswith('author:'):
                author_name = filter_item[7:].strip()
                query = query.join(author_meta_data_alias).join(Author).filter(Author.name.ilike(f'%{author_name}%'))
            
            # Filtrar por título
            elif filter_item.startswith('title:'):
                title_value = filter_item[6:].strip()
                query = query.filter(ds_meta_data_alias.title.ilike(f'%{title_value}%'))
                
            # Filtrar por título o tag (consulta general)
            else:
                query = query.filter(
                    or_(
                        ds_meta_data_alias.title.ilike(f"%{filter_item}%"),
                        ds_meta_data_alias.tags.ilike(f"%{filter_item}%")
                    )
                )

        # Ordenar resultados
        if sorting == "oldest":
            query = query.order_by(DataSet.created_at.asc())
        else:
            query = query.order_by(DataSet.created_at.desc())

        # Ejecutar la consulta y obtener todos los resultados
        results = query.all()

        # Filtrar por tamaño mínimo después de obtener los resultados
        if min_size_filter is not None:
            results = [ds for ds in results if ds.get_file_total_size() >= min_size_filter]

        # Filtrar por tamaño máximo después de obtener los resultados
        if max_size_filter is not None:
            results = [ds for ds in results if ds.get_file_total_size() <= max_size_filter]
            
        if uvl_min.isdigit() or uvl_max.isdigit():
            results = [
                ds for ds in results
                if num_uvls(ds, uvl_min, uvl_max)
            ]

        return results

def num_uvls(dataset, num_min, num_max):
    max_valid = num_max.isdigit()
    min_valid = num_min.isdigit()
    number = dataset.get_files_count()

    if min_valid and max_valid:
        return number >= int(num_min) and number <= int(num_max)
    else:
        return (min_valid and number >= int(num_min)
                or max_valid and number <= int(num_max))
        
        