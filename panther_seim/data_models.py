""" Code for managing data models.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/data-models
"""

from typing import Sequence, Mapping
from ._util import RestInterfaceBase, get_rest_response
from .exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError


class DataModelInterface(RestInterfaceBase):
    """An interface for working with data models in Panther. An instance of this class will be
    attached to the Panther client object.
    """

    def list(self) -> list[dict]:
        """Lists all data models that are configured in Panther.

        Returns:
            A list of data models
        """
        # Get Data Models
        # pylint: disable=duplicate-code
        models = []
        limit = 50
        has_more = True
        cursor = None

        while has_more:
            params = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            resp = self._send_request("get", "data_models", params=params)
            results = get_rest_response(resp)
            cursor = results.get("next")
            has_more = cursor
            models += results.get("results", [])

        return models

    def get(self, model_id: str) -> dict:
        """Returns the data model with the provided ID.

        Args:
            model_id (str): The ID of the data model to fetch.
        """

        resp = self._send_request("get", f"data_models/{model_id}")
        if resp.status_code == 404:
            msg = f"No data model found with ID '{model_id}'"
            raise EntityNotFoundError(msg)
        return get_rest_response(resp)

    @staticmethod
    def _create(  # pylint: disable=too-many-arguments
        body: str = "",
        description: str = "",
        display_name: str = None,
        enabled: bool = None,
        log_types: Sequence[str] = None,
        mappings: Mapping[str, str] = None,
    ) -> dict:
        """Creates a data-model dictionary, which can be sent as-is to update a new data model, or
        used as a base for creating a data model. Since this dictionary creation is identitcal for
        the 'create' and 'update' functions, we centralize the logic here.
        """
        # -- Craft request body
        body = {"body": body}  # Apparently this is required, not sure why
        if description:
            body["description"] = description
        if display_name:
            body["displayName"] = display_name
        if enabled is not None:
            body["enabled"] = enabled
        if log_types:
            body["logTypes"] = log_types
        if mappings:
            # I made a decision here to let the package users specify mappings differently from the
            #   rest api. The API spec says this should be an array of objects with a name field,
            #   and either a path or method field. For simplicity, we let users just have a dict
            #   where the keys are the standard field name, and the values are either a JSON path
            #   or a method name. Nice for them, but we need to convert it to what the API wants.
            body["mappings"] = []
            for k, v in mappings.items():
                mapping = {"name": k}
                if v.startswith("$."):
                    mapping["path"] = v[2:]
                else:
                    mapping["method"] = v
                body["mappings"].append(mapping)

        return body

    def create(  # pylint: disable=too-many-arguments
        self,
        model_id: str,
        body: str = "",
        description: str = "",
        display_name: str = None,
        enabled: bool = None,
        log_types: Sequence[str] = None,
        mappings: Mapping[str, str] = None,
    ) -> dict:
        """Creates a new Data Model.

        Args:
            id (str): the ID of the data model
            body (str, optional): the Python code for the data model, if needed
            description (str, optional): a description for the data model
            display_name (str, optional): the UI display name for the model
                If not speficied, the ID will be used.
            enabled (bool, optional): whether the model is active or not
                default: true
            log_types (list[str], optional): list of log types this data_model associates with
                Note: only 1 data model can be assigned to a log type.
            mappings (dict, optional): mapping of standard fields to log fields
                The dictionary keys are the name of the standard field.
                The dictionary values are either a Python method name, or a JSON path.
                JSON paths must start with "$.", while Python methods need not.

        Returns:
            The created data model object.
        """
        payload = DataModelInterface._create(
            body, description, display_name, enabled, log_types, mappings
        )
        payload["id"] = model_id

        # -- Invoke API
        resp = self._send_request("POST", "data_models", body=payload)
        if resp.status_code == 400:
            raise PantherError(f"Invalid data model: {resp.text}")
        if resp.status_code == 409:
            msg = f"Data Model ID '{model_id}' is already in use"
            raise EntityAlreadyExistsError(msg)
        return get_rest_response(resp)

    def update(  # pylint: disable=too-many-arguments
        self,
        model_id: str,
        new_id: str = None,
        body: str = "",
        description: str = "",
        display_name: str = None,
        enabled: bool = None,
        log_types: Sequence[str] = None,
        mappings: Mapping[str, str] = None,
        update_only: bool = False,
    ) -> dict:
        """Updates an existing Data Model.

        Args:
            id (str): the ID of the data model
            new_id (str, optional): A new model ID, if you want to change it
            body (str, optional): the Python code for the data model, if needed
            description (str, optional): a description for the data model
            display_name (str, optional): the UI display name for the model
                If not speficied, the ID will be used.
            enabled (bool, optional): whether the model is active or not
                default: true
            log_types (list[str], optional): list of log types this data_model associates with
                Note: only 1 data model can be assigned to a log type.
            mappings (dict, optional): mapping of standard fields to log fields
                The dictionary keys are the name of the standard field.
                The dictionary values are either a Python method name, or a JSON path.
                JSON paths must start with "$.", while Python methods need not.
            update_only (bool, optional): raise an error if the data model doesn't exist
                By default, if you try to update a data model that doesn't exist, we simply create
                a new model according to the parameters passed in. If this behaviour is undesirable
                then set update_only to False.

        Returns:
            The created data model object.
        """
        # -- Check if exists
        if update_only:
            self.get(model_id)  # Will raise EntityNotFound if the item doesn't exist yet

        # -- Craft Payload
        payload = DataModelInterface._create(
            body, description, display_name, enabled, log_types, mappings
        )
        payload["id"] = new_id or model_id

        # -- Invoke API
        resp = self._send_request("PUT", f"data_models/{model_id}", body=payload)
        if resp.status_code == 400:
            raise PantherError(f"Invalid data model: {resp.text}")
        return get_rest_response(resp)

    def delete(self, model_id: str) -> None:
        """Deletes a data model.

        Args:
            id (str): the ID of the model to delete.
        """

        resp = self._send_request("DELETE", f"data_models/{model_id}")
        match resp.status_code:
            case 204:
                return
            case 400:
                raise PantherError(f"Invalid delete request: {resp.text}")
            case 404:
                raise EntityNotFoundError(
                    f"Cannot delete model with ID {model_id}; ID does not exist"
                )

        # If none of the status codes above matched, then this is an unknown error.
        raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")
