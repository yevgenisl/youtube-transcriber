***Settings***
Library    RequestsLibrary
Library    Process
Suite Setup    Start Flask App
Suite Teardown    Stop Flask App

***Variables***
${BASE_URL}    http://localhost:5002/api
&{EMPTY_DICT}    Create Dictionary

***Keywords***
Start Flask App
    Log    Starting Flask Application    console=True
    Start Process    python front-end/app.py    alias=flask_app    stdout=${OUTPUT_DIR}/flask_stdout.log    stderr=${OUTPUT_DIR}/flask_stderr.log
    Sleep    3s  # Wait for the Flask app to initialize
    Create Session    flask_api    ${BASE_URL}

Stop Flask App
    Log    Stopping Flask Application    console=True
    Terminate Process    flask_app    # Send SIGTERM
    Delete All Sessions

***Test Cases***
Get All Words
    [Documentation]    Test GET /api/words endpoint
    ${response}=    GET On Session    flask_api    /words
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be True    isinstance(${json_response}, list)

Get Chosen Words
    [Documentation]    Test GET /api/chosen_words endpoint
    ${response}=    GET On Session    flask_api    /chosen_words
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be True    isinstance(${json_response}, list)

Get Last Viewed Videos
    [Documentation]    Test GET /api/last_viewed_videos endpoint
    ${response}=    GET On Session    flask_api    /last_viewed_videos
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be True    isinstance(${json_response}, list)

Save Words
    [Documentation]    Test POST /api/save endpoint
    @{words_to_save}=    Create List    word1    word2
    &{payload}=    Create Dictionary    words=${words_to_save}
    ${response}=    POST On Session    flask_api    /save    json=${payload}
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be Equal As Strings    ${json_response}[status]    success

Get Next Set Of Words
    [Documentation]    Test GET /api/next_set_of_words?video_id=test_video
    ${response}=    GET On Session    flask_api    /next_set_of_words?video_id=test_video
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be True    isinstance(${json_response}, list)

Translate Word
    [Documentation]    Test POST /api/translate endpoint
    &{payload}=    Create Dictionary    word=hello
    ${response}=    POST On Session    flask_api    /translate    json=${payload}
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Contain    ${json_response}    translation

Search Sentences
    [Documentation]    Test GET /api/search_sentences?word=test_word&video_id=test_video
    ${response}=    GET On Session    flask_api    /search_sentences?word=test_word&video_id=test_video
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Contain    ${json_response}    sentences
    Should Be True    isinstance(${json_response}[sentences], list)

Get Video Metadata
    [Documentation]    Test GET /api/video_metadata?video_id=test_video
    ${response}=    GET On Session    flask_api    /video_metadata?video_id=test_video
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Contain    ${json_response}    title
    # Add other expected keys like 'channel', 'thumbnail_url' etc. if applicable

Get Last Viewed Video
    [Documentation]    Test GET /api/last_viewed_video endpoint
    ${response}=    GET On Session    flask_api    /last_viewed_video
    Should Be Equal As Strings    ${response.status_code}    200
    # Response might be null or a video object, basic status check is enough for now

Delete Video
    [Documentation]    Test POST /api/delete_video endpoint
    &{payload}=    Create Dictionary    video_id=test_video_to_delete
    ${response}=    POST On Session    flask_api    /delete_video    json=${payload}
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be Equal As Strings    ${json_response}[status]    success

Delete Chosen Words
    [Documentation]    Test POST /api/delete_chosen_words endpoint
    @{words_to_delete}=    Create List    word1_to_delete
    &{payload}=    Create Dictionary    words=${words_to_delete}
    ${response}=    POST On Session    flask_api    /delete_chosen_words    json=${payload}
    Should Be Equal As Strings    ${response.status_code}    200
    ${json_response}=    To Json    ${response.content}
    Should Be Equal As Strings    ${json_response}[status]    success

Export Words
    [Documentation]    Test POST /api/export_words endpoint
    &{word1}=    Create Dictionary    word=hello    translation=hola
    &{word2}=    Create Dictionary    word=world    translation=mundo
    @{words_to_export}=    Create List    ${word1}    ${word2}
    &{payload}=    Create Dictionary    words=${words_to_export}
    ${response}=    POST On Session    flask_api    /export_words    json=${payload}
    Should Be Equal As Strings    ${response.status_code}    200
    Should Be Equal As Strings    ${response.headers}[Content-Type]    text/csv; charset=utf-8
    # For actual content check, one might save the response.content and verify CSV structure/content
    Should Not Be Empty    ${response.content}
