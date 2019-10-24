
$(document).ready(function() {

    // always update recommendations on pageload
    update_rec();

    $('.doneBtn').on('click', function() {
        $.ajax({
            url: "/done",
            method: "POST",
            data: JSON.stringify($(this).attr("id")),
            contentType: 'application/json;charset=UTF-8',
            success: function(data) {
                console.log(data);
                //$('#evalModal').modal('show')
                //TODO on success open modal?
            }
        });
    });

    $('.allZeroBtn').on('click', function() {
        $.ajax({//
            url: "/allzero",
            method: "POST",
            data: JSON.stringify($(this).attr("id")), // TODO id call needed?
            contentType: 'application/json;charset=UTF-8',
            success: function(data) {
                //console.log(data);
                artistplays = data['plays_data'];
                $('tbody > tr > td:nth-child(2)').each(function(index, element) {
                    //console.log(element);
                    element.innerText = 0;
                });
                // dont update
                update_rec()
            }
        });
    });


   $('.restartBtn').on('click', function() {
       $.ajax({
           url: "/restart",
           method: "POST",
           data: JSON.stringify($(this).attr("id")), // TODO id call needed?
           contentType: 'application/json;charset=UTF-8',
           success: function () {
               console.log("restart successfully");
               window.location.reload();
           }
       });

   });


    $('.btnUp').on('click', function() {
        $.ajax({
            url: "/buttonup",
            method: "POST",
            data: JSON.stringify($(this).attr("id")),
            contentType: 'application/json;charset=UTF-8',
            success: function(data) {
                //console.log(data);
                artistplays = data['plays_data'];
                $('tbody > tr > td:nth-child(2)').each(function(index, element) {
                    //console.log(element);
                    element.innerText = artistplays[index];
                });
                update_rec()
            }
        });
    });

    $('.btnDn').on('click', function() {
        $.ajax({
            url: "/buttondown",
            method: "POST",
            data: JSON.stringify($(this).attr("id")),
            contentType: 'application/json;charset=UTF-8',
            success: function(data) {
                console.log(data);
                artistplays = data['plays_data'];
                $('tbody > tr > td:nth-child(2)').each(function(index, element) {
                    //console.log(element);
                    element.innerText = artistplays[index];
                });
                update_rec()
            }
        });
    });


    function update_rec() {
        $.ajax({
            type: "GET",
            url: "/api/recommendations",
            data: 'json',
            success: function (response) {
                console.log(response);
                recommendations = response['recommendations'];
                $('#recommendationBox').html('');
                var count = 1;
                for(var k in recommendations) {
                    //console.log(type(recommendations))
                    //console.log(recommendations)
                    //$('#recommendationBox').append("<h3>"+r+"</h3>"+r[0]);
                    $('#recommendationBox').append("<tr><td>" + count +"</td><td>" + k + "</td><td>" + recommendations[k].slice(1,2)+ "</td><td>"+ recommendations[k].slice(2,3) +"</td></tr>");
                    count += 1
                }

            },
            error: function () {
                //console.log("error...")
                alert('Error while Sending request..');
            }
        });
    }

});