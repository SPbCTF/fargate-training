require './model'
require './apology_util'
require 'sinatra/base'
require 'haml'

module ApplicationHelper

  def forbidden!
    return if authorized?
    halt 403, "Только для извинённых\n"
  end


  def protected!
    return if authorized?
    headers['WWW-Authenticate'] = 'Basic realm="Restricted Area"'
    halt 401, "Зайди и извинись!\n"
  end


  def get_cred()
      return Rack::Auth::Basic::Request.new(request.env)
    end


  def authorized?
    @auth ||=  get_cred()
    begin
      user = User.get(@auth.credentials[0])
      @auth.provided? and @auth.basic? and @auth.credentials and user.authenticate(@auth.credentials[1])
    rescue
      return false
    end
  end


  def new_user(username, password)
    if username.empty? or password.empty? or username =~ /[^A-Za-z0-9\-]/
      return false
    end 
    begin  
      user = User.new(:username => username, :password => password)
      user.save
    rescue DataObjects::IntegrityError => msg
      if msg.message.include? "UNIQUE constraint failed"
        return false
      else
        return true
      end
    end
  end
  
end


class Auth_main < Sinatra::Base  
  disable :show_exceptions
  helpers ApplicationHelper


  # Войти
  get '/login' do
    protected!
    redirect to("/")
  end


  # Выйти
  get '/logout' do
    if authorized?
      status 401
      haml :logout, :locals => {:message => "Успешно попрощались\n"}
    else
      status 404
      haml :logout, :locals => {:message => "Вы уже успешно попрощались\n"}
    end
  end


  # Страница отправки извинения
    get '/apology' do
      forbidden!
      haml :apology
    end


  # Поиск публичных извиненений по пользователю
  get '/apology/find' do
    forbidden!
    nickname_sender = params['nickname_sender']
    puts nickname_sender
    ap = Apology.new(nickname_sender)
    message = ""
    if ap.check_exist_user(nickname_sender)
      res_ap = ap.get_public_apology()
    else
      res_ap = []
      message = "Не сегодня"
    end    
    haml :index, :locals => {:result_find => res_ap, 
                              :nickname_sender => nickname_sender,
                              :message => message}
  end


  # # Прочитать извинение
  get '/apology/read' do
    forbidden!
    nickname_sender = params['nickname_sender']
    id = params['id']
    ap = Apology.new(nickname_sender)
    res_apology = ap.get_public_apology_id(id)
    haml :read_apology, :locals => {:res_apology => res_apology}
  end


  # Отправить извинение:публичное или приватное
  post '/apology' do
    forbidden!
    auth_cred ||=  get_cred()
    nickname_sender = auth_cred.credentials[0]
    nickname_receiver = params['nickname_receiver']
    private = params['private']
    apology_text = params['apology_text']
    ap = Apology.new(nickname_sender)
    ap.add_to_user_apology(nickname_receiver, private, apology_text)
  end

end

class Main < Sinatra::Application
  use Auth_main
  disable :show_exceptions
  helpers ApplicationHelper

  # Главная страница
  get '/' do
    haml :index
  end


  # Ошибка с рандомным извинением
  error 404 do
    haml :error
  end


  # Страница регистрации
  get '/register' do
    haml :register
  end


  # Запрос на регистрацию
  post '/register' do
    username = params['username']
    password = params['password']
    if new_user(username, password)
      haml :index, :locals => {:message => "Добрый день #{username}, не желаете извиниться?"}
    else
      haml :index, :locals => {:message => "Вам отказано в возможности извиниться!"}
    end
  end
end

# Действия чекера:
# Чекер регистрирует пользователя для извинений aka test1
# Регистируеет второго пользователя aka test2
# Из под пользователя test2 извиняется перед test1 с пометкой 'Приватное извинение'

# Проверка функциональности сервиса:
# Регистрация
# Авторизация 
# Ошибка 404