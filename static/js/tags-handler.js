
const tagContainer = document.querySelector('.tag-holder')

const input = document.querySelector('.input-search-cls')

var tags = [];
var allowed_list = [];



function createTags(label,isAllowed){
	const div = document.createElement('div');
	const span_tagname = document.createElement('span');
	const span_minus = document.createElement('span');
	const span_closeIcon = document.createElement('span');
	if(isAllowed){
	
		div.setAttribute('class','d-inline-flex tag-container allowed')
		span_tagname.innerHTML = label;
		span_tagname.setAttribute('class','tag-name');
		
		
		span_minus.innerHTML = 'add';
		span_minus.setAttribute('class','material-icons allowed');
		span_minus.setAttribute('data-item',label);
		
		
		span_closeIcon.innerHTML = 'close';
		span_closeIcon.setAttribute('class','material-icons tag-close');
		span_closeIcon.setAttribute('data-item',label);
	}else{
		div.setAttribute('class','d-inline-flex tag-container not-allowed');
		span_tagname.innerHTML = label;
		span_tagname.setAttribute('class','tag-name');
		
		
		span_minus.innerHTML = 'remove';
		span_minus.setAttribute('class','material-icons not-allowed');
		span_minus.setAttribute('data-item',label);
	
	
		span_closeIcon.innerHTML = 'close';
		span_closeIcon.setAttribute('class','material-icons tag-close');
		span_closeIcon.setAttribute('data-item',label);
	}
	div.appendChild(span_tagname);
	div.appendChild(span_minus);
	div.appendChild(span_closeIcon);
	
	return div;

}

function reset(){
	document.querySelectorAll('.tag-container').forEach(function(tag){
		tag.parentElement.removeChild(tag);
	});
}

function addTags(){
	reset();
	tags.forEach(function(tag){
		const index = tags.indexOf(tag);
		const input_tag = createTags(tag,allowed_list[index]);
		tagContainer.append(input_tag);
	});
}

input.addEventListener('keyup',function(e){
	if(e.key === 'Enter'){
		if(tags.indexOf(input.value)===-1){
			tags.push(input.value);
			allowed_list.push(1);
			addTags();
			
		}input.value = '';
	}
})

document.addEventListener('click',function(e){
	if(e.target.className ==='material-icons tag-close'){
		const value = e.target.getAttribute('data-item');
		const index = tags.indexOf(value);
		tags = [...tags.slice(0,index),...tags.slice(index+1)];
		allowed_list = [...allowed_list.slice(0,index),...allowed_list.slice(index+1)];
		addTags();
	}
	if(e.target.className === 'material-icons allowed'){
		e.target.parentElement.classList.remove('allowed');
		e.target.parentElement.classList.add('not-allowed');
		e.target.classList.remove('allowed');
		e.target.classList.add('not-allowed');
		e.target.innerHTML = "remove";
		var index = tags.indexOf(e.target.getAttribute("data-item"));
		allowed_list[index] = 0;
		console.log(allowed_list);
	}
	else if(e.target.className === 'material-icons not-allowed'){
		e.target.parentElement.classList.remove('not-allowed');
		e.target.parentElement.classList.add('allowed');
		e.target.classList.remove('not-allowed');
		e.target.classList.add('allowed');
		e.target.innerHTML = "add";
		allowed_list[tags.indexOf(e.target.getAttribute("data-item"))] = 1;
	}
});