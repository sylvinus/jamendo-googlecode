Jamendo.music = {

	playByTag:function(tagName) {
		return Jamendo.music.playByGet2("/track//",{"tag_idstr":tagName});
	},
	
	playByGet2:function(path,params,callback,options) {
		return Jamendo.get2("stream+"+path,params,function(data) {
			
			Jamendo.audio.playMP3(data[0].stream);
			
			if (callback) callback(data);
		},options);}
	
	},


};