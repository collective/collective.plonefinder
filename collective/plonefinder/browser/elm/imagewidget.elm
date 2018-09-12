port module ImageWidget exposing (main)

import Browser exposing (element)
import Html exposing (Attribute, button, div, img, input, text)
import Html.Attributes exposing (id, name, src, type_, value)
import Html.Events exposing (preventDefaultOn)
import Json.Decode as Decode


main =
    element
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
    { widgetId : WidgetId
    , inputId : InputId
    , relativeUrl : RelativeUrl
    , portalUrl : PortalUrl
    }


init :
    { widgetId : String
    , inputId : String
    , relativeUrl : String
    , portalUrl : String
    }
    -> ( Model, Cmd Msg )
init flags =
    let
        widgetId =
            WidgetId flags.widgetId

        inputId =
            InputId flags.inputId

        relativeUrl =
            RelativeUrl flags.relativeUrl

        portalUrl =
            PortalUrl flags.portalUrl
    in
    ( Model widgetId inputId relativeUrl portalUrl, Cmd.none )


hasImage : Model -> Bool
hasImage model =
    let
        (RelativeUrl url) =
            model.relativeUrl
    in
    if url == "" then
        False

    else
        True


absoluteImageUrl : Model -> String
absoluteImageUrl model =
    let
        (RelativeUrl relativeUrl) =
            model.relativeUrl

        (PortalUrl portalUrl) =
            model.portalUrl
    in
    portalUrl ++ "/resolveuid/" ++ relativeUrl



-- UPDATE


type Msg
    = RemoveImage
    | SetRelativeUrl RelativeUrl
    | OpenFinder


port openfinder : String -> Cmd msg


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        (WidgetId widgetId) =
            model.widgetId
    in
    case msg of
        RemoveImage ->
            ( { model | relativeUrl = RelativeUrl "" }, Cmd.none )

        OpenFinder ->
            ( model, openfinder widgetId )

        SetRelativeUrl relativeUrl ->
            ( { model | relativeUrl = relativeUrl }, Cmd.none )



-- SUBSCRIPTIONS


port relativeUrlPort : (String -> msg) -> Sub msg


subscriptions : Model -> Sub Msg
subscriptions model =
    relativeUrlPort (\relativeUrl -> SetRelativeUrl (RelativeUrl relativeUrl))



-- VIEW


onClickPreventDefault : msg -> Attribute msg
onClickPreventDefault msg =
    preventDefaultOn "click" (Decode.map alwaysPreventDefault (Decode.succeed msg))


alwaysPreventDefault : msg -> ( msg, Bool )
alwaysPreventDefault msg =
    ( msg, True )


view : Model -> Html.Html Msg
view model =
    div []
        [ field model, buttons model, image model ]


field model =
    let
        (InputId inputId) =
            model.inputId

        (RelativeUrl relativeUrl) =
            model.relativeUrl
    in
    input [ type_ "hidden", id inputId, name inputId, value relativeUrl ] []


buttons model =
    div []
        [ browseButton model, removeButton model ]


browseButton model =
    button [ onClickPreventDefault OpenFinder ] [ text "Browse server" ]


removeButton model =
    if hasImage model then
        button [ onClickPreventDefault RemoveImage ] [ text "Remove" ]

    else
        text ""


image model =
    let
        imageUrl =
            absoluteImageUrl model
    in
    if hasImage model then
        div []
            [ img [ src imageUrl ] [] ]

    else
        div []
            [ text "No Image" ]
