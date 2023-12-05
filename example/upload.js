const fs = require('fs').promises;
const axios = require('axios');
const path = require('path');

const filePath = 'D:\\test.safetensors';
const chunkSize = 1 * 1024 * 1024; // 1MB
const credentials = 'admin:123456';
const Authorization = `Basic ${Buffer.from(credentials).toString('base64')}`;
const headers = { Authorization };

async function uploadChunk(content, chunkNumber, filename) {
    const body = {
        filename,
        chunkNumber,
        content,
        modelType: 'lora',
    };

    try {
        const response = await axios.post(
            'http://127.0.0.1:7860/myapi/model',
            body,
            { headers: headers }
        );
        console.log(`Chunk ${chunkNumber} uploaded, status:`, response.status);
    } catch (error) {
        console.error(`Error uploading chunk ${chunkNumber}:`, error);
        throw error; // Optional: Throw error to stop the process
    }
}

async function uploadFile(filePath) {
    try {
        const data = await fs.readFile(filePath);
        const totalChunks = Math.ceil(data.length / chunkSize);
        const filename = path.basename(filePath);

        for (let i = 0; i < totalChunks; i++) {
            const chunk = data.slice(i * chunkSize, (i + 1) * chunkSize);
            const content = chunk.toString('base64');
            let chunkNumber = i + 1;

            if (i === totalChunks - 1) {
                chunkNumber = -1;
            }

            await uploadChunk(content, chunkNumber, filename);
        }
    } catch (err) {
        console.error('Error processing file:', err);
    }
}

uploadFile(filePath);
