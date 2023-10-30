let input = document.querySelector(('#name'));
let log = document.querySelector('#log');
input.addEventListener('input', async function() 
{
    let response = await fetch('/namecheck?q=' + input.value)
    let registrants = await response.json();
    if(input.value != "")
    {
        if (registrants.length > 0)
        {
            log.classList.remove("success-text");
            log.classList.add("error-text");
            log.innerHTML = "Name already taken!";
        }
        else 
        {

            log.classList.remove("error-text");
            log.classList.add("success-text");
            log.innerHTML = "Name avaliable!";
        }
    }
    else
    {
        log.classList.remove("success-text");
        log.classList.add("error-text");
        log.innerHTML = "Namefield is Empty!";
    }
});