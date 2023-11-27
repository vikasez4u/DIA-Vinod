
var express = require('express');
const app = express();
const port = 3000;
var multer = require('multer');
var upload = multer({dest:'DIA'});
var storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, 'E:/Projects/DIAWorkspace/DIA/uploads/');
     },
    filename: function (req, file, cb) {
        cb(null , file.originalname);
    }
});
var upload = multer({ storage: storage })

app.use(function (req, res, next) {

    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();
});

app.post('/upload_files', upload.single('file'), (req, res, error) => {
    try {
      console.log(req.file);
      //res.sendStatus(200);
	  //res.json({ message: "Successfully uploaded files" });
	  res.setHeader("Content-Type", "text/html");
	  res.status(200).json({ message: "Successfully uploaded files" });
//	  res.write("<p>Hello World</p>");
	  
    }catch(err) {
		console.log(err);
      res.sendStatus(400);
    }
  });
app.get('/', (req, res) => {
    res.sendStatus('hello Guys');
});
app.listen(port, () => {
    console.log('listening to the port: ' + port);
});