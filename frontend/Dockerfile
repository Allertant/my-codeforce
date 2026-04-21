FROM node:22

WORKDIR /app/frontend

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制前端代码
COPY . .

EXPOSE 5173

# 使用 --host 允许外部访问
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
