require 'nokogiri'

class Apology

  def initialize(nickname_sender)
    @nickname_sender = nickname_sender
    @name_file = nickname_sender.split("\n")[0]   
  end
  
  def get_random_id
    return [*('A'..'Z'),*('a'..'z'),*('0'..'9')].shuffle[0,10].join
  end

  def add_to_user_apology(nickname_receiver, private, apology_text)
    if File.file?("apology/#{@nickname_sender}.xml")
      sender_apologies_file = parse_file()
      sender_apologies_file.xpath("//apologies/*[last()]").each do |node|
        new_apology = Nokogiri::XML::Node.new "apology", sender_apologies_file
        new_apology_text = Nokogiri::XML::Node.new "apology_text", sender_apologies_file
        new_apology_text.content = apology_text
        # new_id = sender_apologies_file.xpath("//apologies/*").count + 1
        new_apology["id"] = get_random_id
        new_apology["private"] = private
        new_apology["nickname_receiver"] = nickname_receiver
        new_apology.add_child(new_apology_text)
        node.add_next_sibling(new_apology)
      end
      self.write_to_file(sender_apologies_file)
    else
      builder = Nokogiri::XML::Builder.new do |xml|
        xml.doc.create_internal_subset(@name_file,
          "-//W3C//DTD HTML 4.01 Transitional//EN",
          "http://www.w3.org/TR/html4/loose.dtd")
        xml.root {
          xml.apologies {
            xml.apology('id' => get_random_id, 'private' => private, 'nickname_receiver' => nickname_receiver) do
              xml.apology_text apology_text
            end
          }
        }
      end
      self.write_to_file(builder.to_xml)
    end
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

  def get_public_apology_id(id)
    return self.parse_file.xpath("//apologies/apology[@private='false' and @id='#{id}']/apology_text/text()")
  end


  def get_public_apology()
    tmp_out_text = []
    self.parse_file.xpath("//apologies/apology[@private='false']/@nickname_receiver").each do |node|
      tmp_out_text.push(node.to_str)
    end
    tmp_out_id = []
    self.parse_file.xpath("//apologies/apology[@private='false']/@id").each do |node|
      tmp_out_id.push(node.to_str)
    end
    return tmp_out_text.zip(tmp_out_id)
  end


  def read(file_name)
    file = File.new("apology/#{file_name}.xml")
    doc = REXML::Document.new file
    puts doc.to_s
  end
  
end
# name = """admin
# <!DOCTYPE foo[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM 'file:////home/texh0k0t/kek'>]>"""
# puts name.split("\n")[0]
ap = Apology.new("aaa-bbb-ccc")
# file = ap.parse_file()
# new_id = file.xpath("//apologies/*").count + 1
# ap.add_to_user_apology("Jack", "false", "HAX1")
# ap.add_to_user_apology("Jack", "true", "FLAG=")
# ap.add_to_user_apology("LOX", "false", "NOPE")
# puts ap.parse_file()
# name_exploit = "KKKS_']/../apology[@private='true"
# print ap.get_public_apology()
puts ap.get_public_apology_id("l3h5OnFDQZ']/../apology[@private='true")