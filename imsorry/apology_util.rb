require 'nokogiri'

class Apology

  def initialize(nickname_sender)
    @nickname_sender = nickname_sender
    @name_file = nickname_sender.split("\n")[0]   
  end
  

  def get_random_id
    return [*('A'..'Z'),*('a'..'z'),*('0'..'9')].shuffle[0,10].join
  end


  def add_to_user_apology(nickname, private, apology_text, direction)
    if File.file?("apology/#{@nickname_sender}.xml")
      sender_apologies_file = parse_file()
      sender_apologies_file.xpath("//apologies[@direction='#{direction}']").each do |node|
        new_apology = Nokogiri::XML::Node.new "apology", sender_apologies_file
        new_apology_text = Nokogiri::XML::Node.new "apology_text", sender_apologies_file
        new_apology_text.content = apology_text
        new_apology["id"] = get_random_id
        new_apology["private"] = private
        new_apology["nickname"] = nickname
        new_apology.add_child(new_apology_text)
        node.add_child(new_apology)
      end
      self.write_to_file(sender_apologies_file)
    else
      builder = Nokogiri::XML::Builder.new do |xml|
        xml.doc.create_internal_subset(@nickname_sender,
          "-//W3C//DTD HTML 4.01 Transitional//EN",
          "http://www.w3.org/TR/html4/loose.dtd")
        xml.root {
          xml.apologies('direction' => "out") do
            if direction == "out"
              xml.apology('id' => get_random_id, 'private' => private, 'nickname' => nickname) do
                xml.apology_text apology_text
              end
            end
          end
          xml.apologies('direction' => "in") do
            if direction == "in"
              xml.apology('id' => get_random_id, 'private' => private, 'nickname' => nickname) do
                xml.apology_text apology_text
              end
            end
          end
        }
      end
      self.write_to_file(builder.to_xml(save_with: Nokogiri::XML::Node::SaveOptions::NO_EMPTY_TAGS))
    end
  end

  def add_to_user_apology_crutch(nickname, private, apology_text)
      add_to_user_apology(nickname, private, apology_text, "out")
      nickname_recivier = @nickname_sender
      initialize(nickname)
      add_to_user_apology(nickname_recivier, private, apology_text, "in")
  end

  def write_to_file(text)
    File.open("apology/#{@name_file}.xml", 'w') {|file|file.write(text)}
  end


  def parse_file()
    return File.open("apology/#{@name_file}.xml"){
    |f|Nokogiri::XML(f) do |config|config.noent end
    }
  end


  def check_exist_user(nickname_sender)
    begin
      return Dir["./apology/*"].include? "./apology/#{nickname_sender}.xml"
    rescue
      return false
    end
  end


  def get_public_apology_out_text_by_id(id)
    return self.parse_file.xpath("//apologies[@direction='out']/apology[@private='false' and @id='#{id}']/apology_text/text()")
  end

  def get_private_apology_out_text_by_id(id)
    return self.parse_file.xpath("//apologies[@direction='in']/apology[@id='#{id}']/apology_text/text()")
  end

  def get_public_apology()
    tmp_out_text = []
    self.parse_file.xpath("//apologies[@direction='out']/apology[@private='false']/@nickname").each do |node|
      tmp_out_text.push(node.to_str)
    end
    tmp_out_id = []
    self.parse_file.xpath("//apologies[@direction='out']/apology[@private='false']/@id").each do |node|
      tmp_out_id.push(node.to_str)
    end
    return tmp_out_text.zip(tmp_out_id)
  end


  def get_input_apology()
    tmp_out_id = []
    self.parse_file.xpath("//apologies[@direction='in']/apology/@id").each do |node|
      tmp_out_id.push(node.to_str)
    end
    tmp_out_nickname = []
    self.parse_file.xpath("//apologies[@direction='in']/apology/@nickname").each do |node|
      tmp_out_nickname.push(node.to_str)
    end
    tmp_out_private = []
    self.parse_file.xpath("//apologies[@direction='in']/apology/@private").each do |node|
      tmp_out_private.push(node.to_str)
    end
    tmp_out_text = []
    self.parse_file.xpath("//apologies[@direction='in']/apology/apology_text/text()").each do |node|
      tmp_out_text.push(node.to_str)
    end
    return tmp_out_id.zip(tmp_out_nickname,tmp_out_private,tmp_out_text)
  end


  def read(file_name)
    file = File.new("apology/#{file_name}.xml")
    doc = REXML::Document.new file
    puts doc.to_s
  end
  
end

# ap = Apology.new("admin")
# ap.