update_goods_amount()

// 计算商品的总价格
function update_goods_amount() {
    // 获取商品的单价和数量
    price = $('.show_pirze').children('em').text()
    count = $('.num_show').val()

    // 计算商品的总价
    price = parseFloat(price)
    count = parseInt(count)
    amount = price*count

    // 设置商品的总价
    $('.total').children('em').text(amount.toFixed(2)+'元')
}

// 增加商品的数量
$('.add').click(function () {
    // 获取商品原有的数目
    count = $('.num_show').val()
    // 加1
    count = parseInt(count)+1
    // 重新设置商品的数目
    $('.num_show').val(count)
    // 更新商品的总价
    update_goods_amount()
})

// 减少商品的数量
$('.minus').click(function () {
    // 获取商品原有的数目
    count = $('.num_show').val()

    // 减1
    count = parseInt(count)-1
    if (count <= 0){
        count = 1
    }
    // 重新设置商品的数目
    $('.num_show').val(count)
    // 更新商品的总价
    update_goods_amount()
})

// 手动输入商品的数量 失去焦点
$('.num_show').blur(function () {
    // 获取用户输入的数目
    count = $(this).val()

    // 校验count是否合法
    if (isNaN(count) || count.trim().length==0 || parseInt(count) <=0){
        count = 1
    }
    // 重新设置商品的数目
    $(this).val(parseInt(count))
    // 更新商品的总价
    update_goods_amount()
})

// 获取add_cart div元素左上角的坐标
var $add_x = $('#add_cart').offset().top;
var $add_y = $('#add_cart').offset().left;

// 获取show_count div元素左上角的坐标
var $to_x = $('#show_count').offset().top;
var $to_y = $('#show_count').offset().left;


$('#add_cart').click(function(){
    // 获取商品id和商品数量
    sku_id = $(this).attr('sku_id') // attr prop
    count = $('.num_show').val()
    csrf = $('input[name="csrfmiddlewaretoken"]').val()

    // 组织参数
    params = {'sku_id':sku_id,
              'count':count,
              'csrfmiddlewaretoken':csrf
    }

    // 发起ajax post请求，访问/cart/add, 传递参数:sku_id count
    $.post('/carts/add', params, function (data) {
        if (data.res == 5){
            $(".add_jump").css({'left':$add_y+80,'top':$add_x+10,'display':'block'})
            $(".add_jump").stop().animate({
                'left': $to_y+7,
                'top': $to_x+7},
                "fast", function() {
                    $(".add_jump").fadeOut('fast',function(){
                        // 重新设置用户购物车中商品的条目数
                        $('#show_count').html(data.total_count);
                    });
            });
        }
        //添加失败
        else{
            alert(data.errmsg)
        }
    })
})