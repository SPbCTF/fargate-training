require 'nokogiri'

class Apology

  def initialize(nickname_sender)
    @nickname_sender = nickname_sender    
  end
  
  def add_to_user_apology(nickname_receiver, private, apology_text)
    if File.file?("apology/#{@nickname_sender}.xml")
      sender_apologies_file = parse_file()
      sender_apologies_file.xpath("//apologies/*[last()]").each do |node|
        new_apology = Nokogiri::XML::Node.new "apology", sender_apologies_file
        new_apology_text = Nokogiri::XML::Node.new "apology_text", sender_apologies_file
        new_apology_text.content = apology_text
        new_id = sender_apologies_file.xpath("//apologies/*").count + 1
        new_apology["id"] = new_id
        new_apology["private"] = private
        new_apology["nickname_receiver"] = nickname_receiver
        new_apology.add_child(new_apology_text)
        node.add_next_sibling(new_apology)
      end
      self.write_to_file(sender_apologies_file)
    else
      builder = Nokogiri::XML::Builder.new do |xml|
        xml.root {
          xml.apologies {
            xml.apology('id' => 1, 'private' => private, 'nickname_receiver' => nickname_receiver) do
              xml.apology_text apology_text
            end
          }
        }
      end
      self.write_to_file(builder.to_xml)
    end
  end


  def write_to_file(text)
    File.open("apology/#{@nickname_sender}.xml", 'w') {|file|file.write(text)}
  end


  def parse_file()
    return File.open("apology/#{@nickname_sender}.xml"){|f|Nokogiri::XML(f)}
  end

  def check_exist_user(nickname_sender)
    return Dir["./apology/*"].include? "./apology/#{nickname_sender}.xml"
  end

  def get_public_apology_nickname_receiver(nickname_receiver)
    return self.parse_file.xpath("//apologies/apology[@private='false' and @nickname_receiver='#{nickname_receiver}']/apology_text/text()")
  end


  def get_public_apology()
    tmp_out = []
    self.parse_file.xpath("//apologies/apology[@private='false']/apology_text/text()").each do |node|
      tmp_out.push(node)
    end
    return tmp_out
  end

  def read(file_name)
    file = File.new("apology/#{file_name}.xml")
    doc = REXML::Document.new file
    puts doc.to_s
  end
  
end

# ap = Apology.new("Jack")
# file = ap.parse_file()
# new_id = file.xpath("//apologies/*").count + 1
# ap.add_to_user_apology("KKKS_", "false", "HAX1")
# puts ap.get_public_apology()