# CCT CUSTOMER SERVICE REQUESTS
This section provides a descriptive overview of the concepts and their implementation and of the resources and their use.
## API Description
## HTTP Header Parameters
The header parameters used in this API are defined in:

| Parameter Name  |Description   | Value characteristics  | 
|---|---|---|
| X-Service  | This is the value of the public key issued to the registered consumer by the City. Must be provided as a mandatory parameter in all messages, |  GUID of 32 characters with no punctuation |   
| X-Session    | This is the session key obtained periodically from the City representing the log file entry of a user’s activities. The session identifier must be provided in all calls other than the service that returns the session identifier. |  GUID of 32 characters with no punctuation.  |    
| X-Signature  | This is a hexadecimal string containing a key-hashed message authentication code (HMAC) calculated from the message string using the SHA256 hash algorithm and encoded using base 64.   | Base 64 encoded string containing an HMAC SHA256 authentication code.  |  

## OpenAPI 3.0 Guide

| Property Name | Description                                                                                                                                                                                                                                 | Example                                            | 
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| Tags          | Grouping operation's are performed using tags. You can assign a list of tags to each API operation.                                                                                                                                         | tags: - name: pets                                 |   
| Paths         | Paths are endpoints (resources), such as /users or /reports/summary/, that your API exposes                                                                                                                                                 | paths:/users/{id}                                  |    
| Operations    | Are the HTTP methods used to manipulate these paths, such as GET, POST, PUT                                                                                                                                                                 | paths:/ping: get: responses: '200':description: OK |  
| Parameters    | The parameters are defined in the parameter section of the operation or path.  To describe a parameter,  specify its name, location (in), data type (defined by either schema or content), and other attributes such as Description and Required. | parameters:- in: pathname: userId                  |  
| Path Parameters | Path parameters are variable parts of a URL path.                                                                                                                                                                                           | GET /users/{id}                                    |  
| Components Structure   | Components serve as a container for various reusable definitions – schemas (data models), parameters, responses                                                                                                                             | schemas:,   securitySchemes:                                         |  
                                                                                                                                                                                                                                           |                                                    |  

