# ******************************************************************************************************************
# Author - Nirmallya Mukherjee
# Note - this code is provided as is for education purposes and does not carry any warranty.
#        You can use this code in any way you like at your own risk
# ******************************************************************************************************************

def searchhome():
    return """
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>My Profile</title>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
	<style>
		img {
			border: 1px solid #000;
            float: left;
		}
		.results {
			width: 80%;
			border: 1px white;
			background-color: white;
			margin: auto;
		}
		.blank {
			width: 80%;
			height: 50px;
			border: 1px white;
			background-color: white;
			margin: auto;
		}
	</style>
</head>

<body>

	<nav class="navbar navbar-expand-lg fixed-top navbar-dark bg-dark">
	  <a id="home" class="navbar-brand">Search Page</a>
	  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
		<span class="navbar-toggler-icon"></span>
	  </button>
	  <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
	  </div>
	</nav>
	<div class="row" style="margin-top:100px;">
		<div class="col-md-2"></div>
		<div class="col-md-8 border" style="padding:25px;">
			<h2 class="text-center" style="font-weight:bold; font-family:'Courier New', monospace;"> Search Page</h2>
			<form name="searchForm" method="post" id="searchForm" action="#">
			  <div class="form-group">
				<label for="fullName">Enter Search Terms</label>
				<input type="text" class="form-control" id="searchTerm" name="searchTerm" placeholder="Search Term">
			  </div>
			 
			  <button id="btn_Submit" type="submit" class="btn btn-primary">Submit</button>
			  
			</form>
		<div id="results" class="results"></div>
		</div>
		<div class="col-md-2"></div>
 
	</div>
	<footer class="page-footer font-small fixed-bottom bg-dark">
	  <div class="footer-copyright text-center text-white py-3"> © Powered by:
		<a class="text-white" href="http://www.pointernext.com/">pointernext.com </a>
	  </div>
	</footer>

	<script src="https://code.jquery.com/jquery-3.5.1.min.js" integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=" crossorigin="anonymous"></script>
	<script>

		$(document).ready(function() {
			$("#home").attr('href', './');
			$("#searchForm").attr('action',./search');
		});

		$("#searchForm").submit(function(e) {
			console.log('The form will now be submitted.');
			$('#results').empty();
			e.preventDefault();
			var form = $(this);
			var url = form.attr('action');
			$.ajax({
				type: "POST", url: url,
				data: form.serialize(),
				success: function(resp) {
					console.log(resp);
					console.log("Successful search");
					$.each(resp, function(key, item)
					{
						let title = item.fields.Title;
						let author = item.fields.Author;
						let date = item.fields.Date;
						let summary = item.fields.Summary;
						$('#results').append("<br>Title : " + title);
						$('#results').append("<br>Author : " + author);
						$('#results').append("<br>Date : " + date);
						$('#results').append("<br>Summary : " + summary);
						$('#results').append("<br>Score : " + item._score);
						$('#results').append("<br><br>");
            		});
        		},
				error: function (resp) {
					console.log(resp);
					$('#results').append("<br>No results found");
				},
        	});
		});
	</script>
</body>
</html>
"""
