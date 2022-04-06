var DOMAIN = window.location.origin;

var changeLoadingState = function(isLoading) {
	if (isLoading) {
		document.getElementById('card-submit').disabled = true;
		document.getElementById('card-spinner').classList.remove('d-none');
		document.getElementById('card-button-text').classList.add('d-none');
	} else {
		document.getElementById('card-submit').disabled = false;
		document.getElementById('card-spinner').classList.add('d-none');
		document.getElementById('card-button-text').classList.remove('d-none');
	}
};

fetch('/subscribe-stripe-config/')
	.then(function(result) { return result.json(); })
	.then(function(data) {
	  	// Initialize Stripe.js
	const stripe = Stripe(data.publicKey);

	var cardChangeForm = document.getElementById('subscribe-card-change-form');
	if (cardChangeForm) {

		cardChangeForm.addEventListener('submit', function (event) {
			event.preventDefault();
			changeLoadingState(true);

			fetch('/subscribe-card-change-session/', {
				method: 'POST',
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
				},
				credentials: 'same-origin',
				body: JSON.stringify({
					"domain": DOMAIN,
				})
			}).then(function(result) { return result.json(); }).then(function(data) {
            	stripe.redirectToCheckout(
                	{
                    	sessionId: data.sessionId
                	}
              	);
          	});
        });
	}
});