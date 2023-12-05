# myapi for StableDiffusion

## API Endpoints

### Upload Model

- **URL**: `/myapi/model`
- **Method**: `POST`
- **Auth Required**: Yes (--api-auth admin:123456)
- **Parameters**:
  - `chunkNumber` (int): The number of the file chunk.
  - `content` (str): The base64 encoded content of the file.
  - `filename` (str): The name of the file.
  - `modelType` (str): The type of the model (e.g., "lora", "checkpoint", "vae").
  - `paths` (str): The subdirectory path within the model directory, separated by '/'.
  - `overwrite` (bool): Whether to overwrite the file if it already exists.

### Delete Model

- **URL**: `/myapi/model/{modelName}`
- **Method**: `DELETE`
- **Auth Required**: Yes (--api-auth admin:123456)
- **Path Parameters**:
  - `filename` (str): The name of the model to be deleted.
- **Query Parameters**:
  - `modelType` (str): The type of the model (e.g., "lora", "checkpoint", "vae").
  - `paths` (str): The subdirectory path within the model directory, separated by '/'.

## Extensibility
This FastAPI application can be further extended as needed, such as adding more endpoints or changing existing logic.
