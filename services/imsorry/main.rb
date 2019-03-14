require './model'
require './apology_util'
require 'sinatra/base'
require 'haml'

module ApplicationHelper

  def forbidden!
    return if authorized?
    halt 403, "Только для извинённых\n<div><a href='/'>На главную</a></div>"
  end


  def protected!
    return if authorized?
    headers['WWW-Authenticate'] = 'Basic realm="Restricted Area"'
    halt 401, "Зайди и извинись!\n<div><a href='/'>На главную</a></div>"
  end


  def get_cred()
      return Rack::Auth::Basic::Request.new(request.env)
    end

  def get_top10()
    return List_apology.all(:limit => 10)
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

  def list_users()
    return Dir["./apology/*"].map{|user| user.split('/')[2].split('.')[0]}
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

  def new_apology_top(username_sender, username_receiver)
    begin  
      apology = List_apology.new(:username_sender => username_sender, :username_receiver => username_receiver)
      apology.save
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


  get '/login' do
    protected!
    redirect to("/")
  end


  get '/logout' do
    if authorized?
      status 401
      haml :logout, :locals => {:message => "Успешно попрощались\n"}
    else
      status 404
      haml :logout, :locals => {:message => "Вы уже успешно попрощались\n"}
    end
  end
  

  get '/input_apologies' do
    auth_cred ||=  get_cred()
    nickname_sender = auth_cred.credentials[0]
    ap = Apology.new(nickname_sender)
    if ap.check_exist_user(nickname_sender)
      res_apologies = ap.get_input_apology()
    else
      res_apologies = []
    end
    haml :input_apologies, :locals => {:res_apologies => res_apologies}
  end

  get '/apology' do
    forbidden!
    haml :apology
  end


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


  get '/apology/read' do
    forbidden!
    nickname_sender = params['nickname_sender']
    id = params['id']
    ap = Apology.new(nickname_sender)
    res_apology = ap.get_public_apology_out_text_by_id(id)
    haml :read_apology, :locals => {:res_apology => res_apology}
  end


  get '/apology/read_private' do
    forbidden!
    auth_cred ||=  get_cred()
    nickname_sender = auth_cred.credentials[0]
    ap = Apology.new(nickname_sender)
    if ap.check_exist_user(nickname_sender)
      id = params['id']
      res_apology = ap.get_private_apology_out_text_by_id(id)
    else
      res_apology = ""
    end
    haml :read_apology, :locals => {:res_apology => res_apology}
  end

  post '/apology' do
    forbidden!
    auth_cred ||=  get_cred()
    nickname_sender = auth_cred.credentials[0]
    nickname_receiver = params['nickname_receiver']
    private = params['private']
    apology_text = params['apology_text']
    ap = Apology.new(nickname_sender)
    ap.add_to_user_apology_crutch(nickname_receiver, private, apology_text)
    if private == "false"
      new_apology_top(nickname_sender, nickname_receiver)
    end
    haml :apology, :locals => {:message => "Вы успешно извинились"}
  end

end

class Main < Sinatra::Application
  use Auth_main
  disable :show_exceptions
  helpers ApplicationHelper


  get '/' do
    haml :index, :locals => {:top10 => get_top10()}
  end


  error 404 do
    haml :error, :locals => {:message => "Не нашлось"}
  end


  get '/register' do
    haml :register
  end


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