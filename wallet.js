const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const TronWeb = require('tronweb');
const axios = require('axios');

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

const allowLocalhostOnly = (req, res, next) => {
    const remoteAddress = req.connection.remoteAddress;
    if (remoteAddress === '::ffff:127.0.0.1' || remoteAddress === '::1') {
        next();
    } else {
        res.status(403).send('Forbidden: Only localhost is allowed to access this endpoint.');
    }
};

const fullNode = new TronWeb.providers.HttpProvider("https://api.shasta.trongrid.io");
const solidityNode = new TronWeb.providers.HttpProvider("https://api.shasta.trongrid.io");
const eventServer = new TronWeb.providers.HttpProvider("https://api.shasta.trongrid.io");
const privateKey = "0d6af4d6b513176b622d296d71f76702e62a6202f1db4ef727f7e3a9dcda6269";
const tronWeb = new TronWeb(fullNode, solidityNode, eventServer, privateKey);

const CONTRACT = "TG3XXyExBkPp9nzdajDZsozEu4BkaSJozs";
const MYACCOUNT = "TL1R6YacZuY2dVqNyreWexzb77Ct2QCick";

// 引入文件写入逻辑
async function writeToFile(ACCOUNT, trxbalance, usdtbalance, amount, id, txID) {
    fs.appendFileSync('03jsredata.txt', `ID: ${id}, User Address: ${ACCOUNT}, Amount: ${amount}\n`, 'utf8');
    fs.appendFileSync('06balance.txt', `TRX: ${trxbalance}, USDT: ${usdtbalance}\n`, 'utf8');
    fs.appendFileSync('04jstopydata.txt', `idlove: ${id}, transfer: ${txID}\n`, 'utf8');
}

app.post('/', allowLocalhostOnly, async (req, res) => {
    try {
        console.log('接收到数据:', req.body);

        const receivedData = req.body;

        const ACCOUNT = receivedData.useraddress;
        const amount = receivedData.amount;
        const id = receivedData.id;

        const trueamount = amount * 1000000;

        const { abi } = await tronWeb.trx.getContract(CONTRACT);
        const contract = tronWeb.contract(abi.entrys, CONTRACT);

        const trueusdtbalance = await contract.methods.balanceOf(MYACCOUNT).call();
        const usdtbalance = trueusdtbalance / 1000000;

        let truetrxbalance;

        truetrxbalance = await tronWeb.trx.getBalance('TTSFjEG3Lu9WkHdp4JrWYhbGP6K1REqnGQ');

        const trxbalancelove = truetrxbalance.toString();
        const trxbalance = trxbalancelove / 1000000;

        // 添加条件检查
        if (trxbalance > 40 && usdtbalance >= amount) {
            const resp = await contract.methods.transfer(ACCOUNT, trueamount).send();
            const txID = resp;

            // 将 ACCOUNT 传递给 writeToFile 函数
            await writeToFile(ACCOUNT, trxbalance, usdtbalance, trueamount, id, txID);

            const postData = {
                idlove: id,
                transfer: txID,
            };

            console.log(postData);

            const apiUrl = 'http://localhost:5000/api/transfer-data';

            const apiResponse = await axios.post(apiUrl, postData);
            console.log('Data sent successfully to Flask API:', apiResponse.data);

            res.send('数据接收成功！');
        } else {
            console.log('条件不满足，不执行转账操作。');
            res.status(400).send('条件不满足，不执行转账操作。');
        }
    } catch (error) {
        console.error('错误:', error);
        res.status(500).send('内部服务器错误');
    }
});


app.listen(port, () => {
    console.log(`服务器正在监听端口 ${port}`);
});




