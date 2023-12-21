# Project Outline

## Description

We want to create a Python client for Panther's public API.

## Outline

We expect the following interfaces.

- client
  - alerts
    - list: returns a list of all alerts within a time frame
    - get: returns all details about a particular alert
    - update: alters the metadata of a list of alerts
    - add_comment: add a comment to a particular alert
  - cloud_accounts
    - list: returns a list of all cloud accounts
    - get: returns all details about a particular cloud account
    - create: programtically onboard a new cloud account
    - update: make changes to an existing cloud account
    - delete: remove a cloud account
  - datalake
    - list: returns a list of databses, tables, and columns
    - get: same as above, but for a single database
  - queries
    - execute: run a query
    - results: fetch the results of a query
    - get: return metadata about a query
    - list: returns a list of previously-run queries
  - log_sources
    - list: returns a list of all log sources
    - get: returns all details of a particular log source
    - delete: removes an existing log source
    - create:
      - s3: creates a new S3 log source
    - update:
      - s3: updates the detauls of an S3 log source
  - metrics
    - get: return Panther metrics over a specified time period
  - users:
    - list: returns a list of all users
    - get: returns all details of a specific user
    - create: create a new user invitation
    - update: make changes to an existing user
    - delete: remove an existing user
  - roles:
    - list: returns a list of all user roles
    - get: returns all details of a particular role
    - create: creates a new user role
    - update: make changes to an existing role
    - delete: removes an existing role
  - tokens:
    - rotate: rotate an existing API token

Below, we list the outline for each function. Parameters in **bold** are required.

### alerts
**list**:
- params:
  - **start**: `str, int, datetime`: the earliest date to return alerts from.
  - end: `str, int, datetime`: the latest date to return alerts from. *Default: current time.*
- returns:
  - list:
    - dict:
      - `id`: str
      - `title`: str
      - `severity`: str
      - `status`: str

**get**:
- params
  - **id** `str`: the ID of the alert to retreive.
- returns:
  - dict
    - `id`: str
    - `title`: str
    - `severity`: str
    - `status`: str
    - `assignee`: dict
      - `id`: str
      - `email`: str

**update**:
- params:
  - **ids** `list[str], str`: the IDs of the alerts to update, or a single ID, as a string
  - assignee_id `str`: the ID of the user to set as the assignee (must not be specified with `assignee_email`)
  - assignee_email `str`: the email of the user to set as the assignee (must not be specified with `assignee_id`)
  - status `str`: the status to set the alerts to
- returns:
  - None

**add_comment**:
- params:
  - **id** `str`: the ID of the alert to add this comment to
  - **body** `str`: the body of the comment
  - format `str`: the format of the body. Can be `HTML` or `PLAIN_TEXT` *Default: `HTML`*
- returns:
  - str: the comment ID

### cloud accounts
**list**
- params:
  - *none*
- returns:
  - list
    - dict
      - `awsAccountId`: str
      - `id`: str
      - `label`: str
      - `isRealtimeScanningEnabled`: bool

**get**
- params:
  - **id**: `str`
- returns
  - dict
    - 