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


type RelativeUrl
    = RelativeUrl String


type PortalUrl
    = PortalUrl String


type alias Model =
    { widget_id : WidgetId
    , input_id : InputId
    , relative_url : RelativeUrl
    , portal_url : PortalUrl
    }


init : ( String, String, String, String ) -> ( Model, Cmd Msg )
init flags =
    let
        ( widget_id_s, input_id_s, relative_url_s, portal_url_s ) =
            flags

        widget_id =
            WidgetId widget_id_s

        input_id =
            InputId input_id_s

        relative_url =
            RelativeUrl relative_url_s

        portal_url =
            PortalUrl portal_url_s
    in
        ( Model widget_id input_id relative_url portal_url, Cmd.none )


hasImage : Model -> Bool
hasImage model =
    let
        (RelativeUrl relative_url) =
            model.relative_url
    in
        if relative_url == "" then
            False
        else
            True


absolute_image_url : Model -> String
absolute_image_url model =
    let
        (RelativeUrl relative_url) =
            model.relative_url

        (PortalUrl portal_url) =
            model.portal_url
    in
        portal_url ++ "/resolveuid/" ++ relative_url



-- UPDATE


type Msg
    = RemoveImage
    | SetRelativeUrl RelativeUrl
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
                ( { model | relative_url = (RelativeUrl "") }, Cmd.none )

            OpenFinder ->
                ( model, openfinder widget_id )

            SetRelativeUrl relative_url ->
                ( { model | relative_url = relative_url }, Cmd.none )



-- SUBSCRIPTIONS


port relative_url : (String -> msg) -> Sub msg


subscriptions : Model -> Sub Msg
subscriptions model =
    relative_url (\relative_url -> SetRelativeUrl (RelativeUrl relative_url))



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

        (RelativeUrl relative_url) =
            model.relative_url
    in
        input [ type' "hidden", id input_id, name input_id, value relative_url ] []


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
        image_url =
            absolute_image_url model
    in
        if hasImage model then
            div []
                [ img [ src image_url ] [] ]
        else
            div []
                [ text "No Image" ]
