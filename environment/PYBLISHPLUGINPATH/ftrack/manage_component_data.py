import os

import pyblish.api
import filelink
import clique


class TGBFtrackManageComponentData(pyblish.api.InstancePlugin):
    """Manage the data of the Ftrack components."""

    order = pyblish.api.IntegratorOrder + 1
    label = "Manage Data"
    families = ["ftrack"]

    def process(self, instance):

        for data in instance.data.get("ftrackComponentsList", []):

            location = data.get(
                "component_location",
                instance.context.data["ftrackSession"].pick_location()
            )
            if location["name"] == "ftrack.server":
                continue

            component = data.get("component", None)
            if not component:
                continue

            # Create destination directory
            resource_identifier = location.get_resource_identifier(component)
            if not os.path.exists(os.path.dirname(resource_identifier)):
                os.makedirs(os.path.dirname(resource_identifier))

            collection = instance.data.get("collection", None)
            if collection:
                target_collection = clique.parse(
                    resource_identifier,
                    pattern="{head}{padding}{tail}"
                )

                # Delete existing files if overwriting.
                if data.get("component_overwrite", False):
                    path = os.path.dirname(target_collection.head)
                    for f in os.listdir(path):
                        file_path = os.path.join(path, f).replace("\\", "/")
                        if target_collection.match(file_path):
                            os.remove(file_path)

                for f in collection:
                    if not os.path.exists(f):
                        filelink.create(
                            f,
                            f.replace(
                                collection.head, target_collection.head
                            )
                        )

            output_path = instance.data.get("output_path", "")
            if output_path:
                # Delete existing file if overwriting
                if data.get("component_overwrite", False):
                    if os.path.exists(resource_identifier):
                        os.remove(resource_identifier)

                if not os.path.exists(output_path):
                    filelink.create(output_path, resource_identifier)