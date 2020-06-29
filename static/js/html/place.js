

//支付
$('#order_btn').click(function() {

    addr_id = $('input[name="addr_id"]:checked').val()
    pay_method = $('input[name="pay_style"]:checked').val()
    sku_ids = $(this).attr('sku_ids')
    csrf = $('input[name="csrfmiddlewaretoken"]').val()

    // alert(addr_id + ":" + pay_method+ ':' + sku_ids)
    params = {'addr_id':addr_id,
              'pay_method':pay_method,
              'sku_ids':sku_ids,
              'csrfmiddlewaretoken':csrf}

    $.post('/orders/commit', params, function (data) {
        if (data.res == 5){
            localStorage.setItem('order_finish',2);
            $('.popup_con').fadeIn('fast', function() {
                setTimeout(function(){
                    $('.popup_con').fadeOut('fast', function(){   //显示成功的界面
                        window.location.href = '/users/order/1';
                    });
                },3000)
            });
        }
        else{
            alert(data.errmsg)
        }
    })
});