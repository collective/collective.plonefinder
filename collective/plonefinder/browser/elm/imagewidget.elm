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

type alias Model =
  { fieldid: String
  , hasImage : Bool
  , url : String
  }
type alias Flags =
  (String, String)

init : Flags -> (Model, Cmd Msg)
init flags =
  let 
    (fieldid, url) = flags
  in
    if url == "" 
    then
      (Model fieldid False "", Cmd.none)
    else
      (Model fieldid True url, Cmd.none)

-- UPDATE

type Msg = ResetImage | SetUrl String

port reset: String -> Cmd msg

update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    ResetImage ->
      (model, reset model.fieldid)
    SetUrl image_url ->
      init (model.fieldid, image_url)

-- SUBSCRIPTIONS

port imageurl : (String -> msg) -> Sub msg

subscriptions : Model -> Sub Msg
subscriptions model =
   imageurl SetUrl

-- VIEW

view : Model -> Html.Html Msg
view model =
  div []
    (imageview model)

imageview model =
  if model.hasImage 
  then
    [ div [ onClick ResetImage ] [ text "Reset" ]
    , img [ src model.url ] []
    ]
  else
    [ text "No Image" ]
