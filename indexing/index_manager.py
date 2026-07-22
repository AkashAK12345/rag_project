import config.settings

from llama_index.core import (
    StorageContext,
    load_index_from_storage
)


def load_existing_index():

    storage_context = StorageContext.from_defaults(
        persist_dir="./storage"
    )

    return load_index_from_storage(
        storage_context
    )


def save_index(index):

    index.storage_context.persist(
        persist_dir="./storage"
    )