port module ImageWidget exposing (..)

import Html exposing (div, text, img, a)
import Html.App as Html
import Html.Events exposing (onClick)
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


view : Model -> Html.Html Msg
view model =
    div []
        (div [ onClick OpenFinder ] [ text "Browse server" ]
            :: image_view model
        )


image_view model =
    let
        (Url url) =
            model.url
    in
        if hasImage model then
            [ div [ onClick RemoveImage ] [ text "Remove" ]
            , img [ src url ] []
            ]
        else
            [ text "No Image" ]
