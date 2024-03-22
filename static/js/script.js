// list view and grid view display block and none
const list_view_anchor = document.querySelector('#anchor_list_view');
const grid_view_anchor = document.querySelector('#anchor_grid_view');
const list_view = document.querySelector('#list_view');
const grid_view = document.querySelector('#grid_view');



list_view_anchor.addEventListener('click', () => {
    list_view.style.display = 'block';
    grid_view.style.display = 'none';
});

grid_view_anchor.addEventListener('click', () => {
    list_view.style.display = 'none';
    grid_view.style.display = 'block';
});


    const searchInput = document.querySelector('#id_search');
    const suggestionList = document.querySelector('#suggestion-list');

    searchInput.addEventListener('input', () => {
        // Clear existing suggestions
        while (suggestionList.firstChild) {
            suggestionList.removeChild(suggestionList.firstChild);
        }

        const inputValue = searchInput.value.trim();
        if (inputValue) {
            fetch(`/search/?search=${inputValue}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    data.data.forEach(item => {
                        const anchor = document.createElement('a');
                        anchor.innerText = item;
                        const listItem = document.createElement('li');
                        listItem.appendChild(anchor);
                        suggestionList.appendChild(listItem);
                    });
                })
                .catch(error => console.error('Error:', error));
        }
    });


// *********************************************************************
document.addEventListener('DOMContentLoaded', function () {
    // collection id and price filter working together
    const applyBtn = document.getElementById('apply-btn');

    applyBtn.addEventListener('click', function () {
        const minPriceValue = document.getElementById('id_min_price').value;
        const maxPriceValue = document.getElementById('id_max_price').value;
        const currentUrl = new URL(window.location.href);
        if (currentUrl.searchParams.has('collection_id')) {
            console.log("get there")
            if (currentUrl.searchParams.has('page')) {
                if (minPriceValue || maxPriceValue) {
                    currentUrl.searchParams.set('min_price', minPriceValue);
                    currentUrl.searchParams.set('max_price', maxPriceValue);
                    currentUrl.searchParams.delete('page');
                    window.location.href = currentUrl.toString();
                }
            }
            else {
                if (minPriceValue || maxPriceValue) {
                    currentUrl.searchParams.set('min_price', minPriceValue);
                    currentUrl.searchParams.set('max_price', maxPriceValue);
                    window.location.href = currentUrl.toString();
                }
            }
        }
    });



});