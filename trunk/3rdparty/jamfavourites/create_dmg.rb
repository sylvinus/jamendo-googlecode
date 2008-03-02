#!/usr/local/bin/ruby

def filesize(folder)
	if ( folder !~ /\/(\.){1,2}$/ )
		if File.directory?(folder)
			Dir.new(folder).inject(0) { |sum,file| sum+filesize(folder+"/"+file) }
		else
			File.size(folder)
		end
	else
		0
	end
end

#def create_dmg
	
	#if (ENV["BUILD_STYLE"] == "Release")
	
		root = "/Users/sylvinus/w/jamfavourites/dist"
		app = root+"/jamFavourites.app"
		dmg = root+"/jamFavourites.dmg"
		tmp = "/tmp/jamFavourites.dmg"

		# Delete
		system("cd #{root} && rm *.dmg")

		# Create   
		if system("hdiutil create #{dmg} -size #{filesize(app)+5000*1024} -ov -fs HFS+ -volname jamFavourites")
			
			# Mount
			volume = `hdiutil attach #{dmg}`
			volume_human = /Apple_HFS\s*(.*)/.match(volume)[1]
			volume_sys = /(.*)\s*Apple_partition_scheme/.match(volume)[1]
			
			# Copy files
			`cp DS_Store "#{volume_human}/.DS_Store"`
			`cd "#{volume_human}" && ln -s /Applications Applications`
			`cp -R #{app} "#{volume_human}"`
			
			# UnMount
			`hdiutil detach #{volume_sys}`
			
			# Convert
			`mv "#{dmg}" "#{tmp}"`
			if File.exists?(tmp)
				`hdiutil convert "#{tmp}" -format UDZO -imagekey zlib-level=9 -o "#{dmg}"`
				`rm #{tmp}`
			else
				exit(1)
			end
		end
		
	#end
	
#end