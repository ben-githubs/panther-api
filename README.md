# Panther API Client

This package provides a Panther object, with methods to utilize Panther's GraphQL and Rest API's within your Python code.

## Usage

### Basic Usage

The Panther client object requires 2 parameters to work: a Panther API key, and the domain name of your Panther instance. Note that the API token's permissiosn affect which Python functions you can use successfully.

Once you have a Panther client, you can access various API functions by using the client's interfaces. The following interfaes are currently available for use:

- `Panther.alerts` - List, fetch, add comments to, and update status of Panther alerts
- `Panther.cloud_accounts` - Full CRUDL support for Panther cloud scanning
- `Panther.data_models` - Full CRUDL support for Data Models
- `Panther.databases` - List and read functions for Panther's datalake databases
- `Panther.globals` - CRUDL support for global helpers
- `Panther.metrics` - A variery of funcrions to fetch metric data from Panther
- `Panther.queries` - CRUDL support for managing saved/scheduled queries
- `Panther.roles` - CRUDL support for user roles
- `Panther.rules` - CRUDL support for managing Panther real-time Python rules
- `Panther.sources` - List, fetch, and delete functions for all log sources, and create/update functions for S3 sources
- `Panther.tokens` - Rotate API tokens (including the one used by the Panther client)
- `Panther.users` - List, fetch, and update functions for Panther users

For an example of using the library, see `example.py` in the repository root directory.

### Data Conversion

By default, we ensure any data returned to the user is a primitive Python data type (string, int, float, list, dict, or set). However, it can be useful to perform conversions of certain data types, such as from timestamp strings to datetime objects. You can enable this behavious by setting `auto_convert = True` when creating your Panther client:

```python
panther = panther_seim.Panther(MY_API_TOKEN, MY_API_DOMAIN, auto_convert=True)
```
