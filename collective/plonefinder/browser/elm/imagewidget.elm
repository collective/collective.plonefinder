port module ImageWidget exposing (..)

import Html exposing (div, text, img, button, Attribute)
import Html.App as Html
import Json.Decode as Json
import Html.Events exposing (onWithOptions, Options, defaultOptions)
import Html.Attributes exposing (type', src)


main =
    Html.programWithFlags
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL


type FieldId
    = FieldId String


type Url
    = Url String


type alias Model =
    { fieldid : FieldId
    , url : Url
    }


init : ( String, String ) -> ( Model, Cmd Msg )
init flags =
    let
        ( fieldid_s, url_s ) =
            flags

        fieldid =
            FieldId fieldid_s

        url =
            Url url_s
    in
        ( Model fieldid url, Cmd.none )


hasImage : Model -> Bool
hasImage model =
    let
        (Url url) =
            model.url
    in
        if url == "" then
            False
        else
            True



-- UPDATE


type Msg
    = RemoveImage
    | SetUrl Url
    | OpenFinder


port remove : String -> Cmd msg


port openfinder : String -> Cmd msg


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        (FieldId fieldid) =
            model.fieldid
    in
        case msg of
            RemoveImage ->
                ( model, remove fieldid )

            OpenFinder ->
                ( model, openfinder fieldid )

            SetUrl url ->
                ( { model | url = url }, Cmd.none )



-- SUBSCRIPTIONS


port url : (String -> msg) -> Sub msg


subscriptions : Model -> Sub Msg
subscriptions model =
    url (\url -> SetUrl (Url url))



-- VIEW


onClickPreventDefault : msg -> Attribute msg
onClickPreventDefault message =
    onWithOptions "click" noSubmitOptions (Json.succeed message)


noSubmitOptions : Options
noSubmitOptions =
    { defaultOptions | preventDefault = True }


view : Model -> Html.Html Msg
view model =
    div []
        [ buttons model, image model ]


buttons model =
    div []
        [ browse_button model, remove_button model ]


browse_button model =
    button [ onClickPreventDefault OpenFinder ] [ text "Browse server" ]


remove_button model =
    if hasImage model then
        button [ onClickPreventDefault RemoveImage ] [ text "Remove" ]
    else
        text ""


image model =
    let
        (Url url) =
            model.url
    in
        if hasImage model then
            div []
                [ img [ src url ] [] ]
        else
            div []
                [ text "No Image" ]
