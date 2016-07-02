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

type FieldId = FieldId String

type Url = Url String

type alias Flags =
  (String, String)

type alias Model =
  { fieldid: FieldId
  , hasImage : Bool
  , url : Url
  }

init : Flags -> (Model, Cmd Msg)
init flags =
  let 
    (fieldid, url) = flags
  in
    (make (FieldId fieldid) (Url url), Cmd.none)

make: FieldId -> Url -> Model
make (FieldId fieldid) (Url url) =
    if url == "" 
    then
      Model (FieldId fieldid) False (Url "")
    else
      Model (FieldId fieldid) True (Url url)

-- UPDATE

type Msg = ResetImage | SetUrl Url

port reset: String -> Cmd msg

update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  let 
    (FieldId fieldid) = model.fieldid
  in
  case msg of
    ResetImage ->
      (model, reset fieldid)
    SetUrl url ->
      (make model.fieldid url, Cmd.none)

-- SUBSCRIPTIONS

port imageurl : (String -> msg) -> Sub msg

subscriptions : Model -> Sub Msg
subscriptions model =
   imageurl (\url -> SetUrl (Url url))

-- VIEW

view : Model -> Html.Html Msg
view model =
  div []
    (imageview model)

imageview model =
  let 
    (Url url) = model.url
  in
  if model.hasImage 
  then
    [ div [ onClick ResetImage ] [ text "Reset" ]
    , img [ src url ] []
    ]
  else
    [ text "No Image" ]
