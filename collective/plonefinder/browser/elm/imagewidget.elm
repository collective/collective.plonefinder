port module ImageWidget exposing (main)

import Browser exposing (element)
import Html exposing (Attribute, button, div, img, input, text)
import Html.Attributes exposing (id, name, src, type_, value)
import Html.Events exposing (preventDefaultOn)
import Json.Decode as Json


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
    { widget_id : WidgetId
    , input_id : InputId
    , relative_url : RelativeUrl
    , portal_url : PortalUrl
    }


init :
    { widget_id_s : String
    , input_id_s : String
    , relative_url_s : String
    , portal_url_s : String
    }
    -> ( Model, Cmd Msg )
init flags =
    let
        widget_id =
            WidgetId flags.widget_id_s

        input_id =
            InputId flags.input_id_s

        relative_url =
            RelativeUrl flags.relative_url_s

        portal_url =
            PortalUrl flags.portal_url_s
    in
    ( Model widget_id input_id relative_url portal_url, Cmd.none )


hasImage : Model -> Bool
hasImage model =
    let
        (RelativeUrl url) =
            model.relative_url
    in
    if url == "" then
        False

    else
        True


absolute_image_url : Model -> String
absolute_image_url model =
    let
        (RelativeUrl r_url) =
            model.relative_url

        (PortalUrl p_url) =
            model.portal_url
    in
    p_url ++ "/resolveuid/" ++ r_url



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
            ( { model | relative_url = RelativeUrl "" }, Cmd.none )

        OpenFinder ->
            ( model, openfinder widget_id )

        SetRelativeUrl relative_url ->
            ( { model | relative_url = relative_url }, Cmd.none )



-- SUBSCRIPTIONS


port relative_url_port : (String -> msg) -> Sub msg


subscriptions : Model -> Sub Msg
subscriptions model =
    relative_url_port (\r_url -> SetRelativeUrl (RelativeUrl r_url))



-- VIEW


onClickPreventDefault : msg -> Attribute msg
onClickPreventDefault msg =
    preventDefaultOn "click" (Json.map alwaysPreventDefault (Json.succeed msg))


alwaysPreventDefault : msg -> ( msg, Bool )
alwaysPreventDefault msg =
    ( msg, True )


view : Model -> Html.Html Msg
view model =
    div []
        [ field model, buttons model, image model ]


field model =
    let
        (InputId input_id) =
            model.input_id

        (RelativeUrl r_url) =
            model.relative_url
    in
    input [ type_ "hidden", id input_id, name input_id, value r_url ] []


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
