var projectName = "Кыргыз тилиндеги санарип тексттерди үнгө айландыруу долбоору";
var apprtimesubject = "Аудиону иштеп чыгуу үчүн болжолдуу убакыт: ";
var apprtimeseconds = " секунд";
var buttonValue = "Аудио иштеп чыгуу";

var digits=[
		["",""],
		["бир ","он "],
		["эки ","жыйырма "],
		["үч ","отуз "],
		["төрт ","кырк "],
		["беш ","элүү "],
		["алты ","алтымыш "],
		["жети ","жетимиш "],
		["сегиз ","сексен "],
		["тогуз ","токсон "]
		];


var ranks=["","миң ","миллион ","миллиард ","триллион ","квадриллион "];
var hundred="жүз ";

function make_numbers(text){
	text = text.replace(/ц/g,"тс");
	var numberPattern = /\d+/g;
	var numbers = text.match(numberPattern);
	if (numbers == null || numbers.length == 0) return text;
	var number_words = new Array(numbers.length);
	var nmwith_tails = new Array(numbers.length);
	numbers.sort(function(a, b){return b-a});
	for (var i = 0; i < numbers.length; i++) {
		number_words[i] = inWords(numbers[i]);
		nmwith_tails[i] = makeTails(number_words[i]);
		//Do something
	}
	reg_ex = "";
	for (var i = 0; i < numbers.length; i++) {
		reg_ex = new RegExp(numbers[i]+"-","g");
		text = text.replace(reg_ex, nmwith_tails[i]);
		reg_ex = new RegExp(numbers[i],"g");
		text = text.replace(reg_ex, number_words[i]);
	}

	return text;
}

function inWords (num) {
	
	while(num.length%3!=0) {
        num="0"+num;
    }
	result = read_number(num);
	return result;
	
}

function makeTails (str) {
	var dict = {};
	dict['өл '] = "өлүнчү ";
	dict['ир '] = "иринчи ";
	dict['ки '] = "кинчи ";
	dict['үч '] = "үчүнчү ";
	dict['рт '] = "ртүнчү ";
	dict['еш '] = "ешинчи ";
	dict['ты '] = "тынчы ";
	dict['ти '] = "тинчи ";
	dict['из '] = "изинчи ";
	dict['уз '] = "узунчу ";
	dict['он '] = "онунчу ";
	dict['ма '] = "манчы ";
	dict['рк '] = "ркынчы ";
	dict['үү '] = "үүнчү ";
	dict['ыш '] = "ышынчы ";
	dict['иш '] = "ишинчи ";
	dict['ен '] = "енинчи ";
	dict['үз '] = "үзүнчү ";
	dict['иң '] = "иңинчи ";
	dict['рд '] = "рдынчы ";
	last3 = str.substr(str.length - 3);
	str = str.slice(0, -3);
	str += dict[last3];
	return str;
}

function read_number(number) {
    var loop_count=0;
    var result="";
    
    //3төн кылып бөлүп чык
    for (var i=number.length-3;i>=0;i=i-3) {
        result=read_three(number.substr(i,3),loop_count)+result;
        loop_count++;
    }
    
    if(result=="") { //эчтеке жок болсо
        result="нөл ";
    }
    
    return result;
}


function read_three(number,i) {
    var output;
    var first=number.substr(2,1); //Бир-тогуз
    var second=number.substr(1,1);//Он-Токсон
    var third=number.substr(0,1); //жүз-тогуз жүз
    
    //99га чейин
    output=digits[second][1]+digits[first][0];


    if(third!="0") { 
        output=digits[third][0]+hundred+output;
    }
    
    if(number!="000") { //бош болсо
        output=output+ranks[i];
    }
    
    return output;
}

function ApprTime(text){
	var result = 0;
	var unit = 4;
	var unitMultiplier = 1;
	var words = text.split(' ');
	if (words.length<8) return unit;
	var sentences = text.split(/[;:.!\?]/);
	for(var i=0; i < sentences.length; i++) {
		unitMultiplier = 1;
		//sentence = myTrim(sentences[i]);
		sentence = sentences[i].trim();
		if (sentence.length < 2) continue;
		words = sentence.split(' ');
		if (words.length>6){
			unitMultiplier = Math.ceil(words.length/6);
		}
		result += unit*unitMultiplier;
	}
	return result;
}
























