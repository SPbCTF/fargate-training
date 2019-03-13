require 'rubygems'
require 'data_mapper'
require 'dm-sqlite-adapter'
require 'bcrypt'

DataMapper.setup(:default, "sqlite://#{Dir.pwd}/db.sqlite")

class User
  include DataMapper::Resource
  property :username, String, :length => 3..50, :key => true
  property :password, BCryptHash

  def authenticate(attempted_password)
    if self.password == attempted_password
      true
    else
      false
    end
  end
end

class List_apology
  include DataMapper::Resource
  property :id, Serial, :key => true
  property :username_sender, String  
  property :username_receiver, String
end

DataMapper.finalize
DataMapper.auto_upgrade!