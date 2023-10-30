let input = document.querySelector(('input'));
input.addEventListener('input', async function() 
{
    let response = await fetch('/search?q=' + input.value)
    let registrants = await response.json();
    let html = '';
    for (let id in registrants) {
        let name = registrants[id].name;
        html += '<li>' + name + '</li>';
    }
    document.querySelector('ul').innerHTML = html;
});