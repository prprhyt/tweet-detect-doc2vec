target_id = "";//twitter id入れる
res_str = "";
t_array = new Array();
contents = document.getElementsByClassName("content");
for(var i=0;i<contents.length;++i){
contents_child = contents[i].getElementsByClassName("stream-item-header");
if(undefined===contents_child) continue;
if(contents_child.length<=0) continue;
if(0<=contents_child[0].innerText.indexOf(target_id)){
    console.log(i);
	tmp_child = contents[i].getElementsByClassName("js-tweet-text-container");
	if(undefined===tmp_child) continue;
	if(tmp_child.length<=0) continue;
    t_dict ={tweet:tmp_child[0].innerText};
    t_array.push(t_dict);
}
}
res_str = JSON.stringify(t_array);