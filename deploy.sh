#!/bin/bash

# Vercel 部署脚本

echo "🚀 开始部署到 Vercel..."

# 检查是否安装了 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI 未安装，请先安装："
    echo "npm install -g vercel"
    exit 1
fi

# 检查必要文件
if [ ! -f "vercel.json" ]; then
    echo "❌ 缺少 vercel.json 配置文件"
    exit 1
fi

if [ ! -f "api/app.py" ]; then
    echo "❌ 缺少 api/app.py 文件"
    exit 1
fi

if [ ! -f "requirements-vercel.txt" ]; then
    echo "❌ 缺少 requirements-vercel.txt 文件"
    exit 1
fi

# 创建部署目录
echo "📁 准备部署文件..."
mkdir -p .vercel-deploy
cp -r api .vercel-deploy/
cp -r src .vercel-deploy/
cp -r config .vercel-deploy/
cp requirements-vercel.txt .vercel-deploy/requirements.txt
cp vercel.json .vercel-deploy/

# 进入部署目录
cd .vercel-deploy

# 设置环境变量
echo "🔧 设置环境变量..."
if [ -f "../env.vercel.example" ]; then
    echo "请在 Vercel 控制台设置以下环境变量："
    echo "================================"
    cat ../env.vercel.example
    echo "================================"
fi

# 部署到 Vercel
echo "🚀 开始部署..."
vercel --prod

# 清理临时文件
cd ..
rm -rf .vercel-deploy

echo "✅ 部署完成！"
echo "🌐 请在 Vercel 控制台查看部署状态" 