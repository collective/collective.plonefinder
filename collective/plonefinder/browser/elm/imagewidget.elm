port module ImageWidget exposing (..)

import Html exposing (div, text, img, button, input, Attribute)
import Html.App as Html
import Json.Decode as Json
import Html.Events exposing (onWithOptions, Options, defaultOptions)
import Html.Attributes exposing (type', src, name, id, value)


main =
    Html.programWithFlags
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL


type WidgetId
    = WidgetId String


type InputId
    = InputId String


type Url
    = Url String


type alias Model =
    { widget_id : WidgetId
    , input_id : InputId
    , url : Url
    }


init : ( String, String, String ) -> ( Model, Cmd Msg )
init flags =
    let
        ( widget_id_s, input_id_s, url_s ) =
            flags

        widget_id =
            WidgetId widget_id_s

        input_id =
            InputId input_id_s

        url =
            Url url_s
    in
        ( Model widget_id input_id url, Cmd.none )


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


port openfinder : String -> Cmd msg


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        (WidgetId widget_id) =
            model.widget_id
    in
        case msg of
            RemoveImage ->
                ( { model | url = (Url "") }, Cmd.none )

            OpenFinder ->
                ( model, openfinder widget_id )

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
        [ field model, buttons model, image model ]


field model =
    let
        (InputId input_id) =
            model.input_id

        (Url url) =
            model.url
    in
        input [ type' "hidden", id input_id, name input_id, value url ] []


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
