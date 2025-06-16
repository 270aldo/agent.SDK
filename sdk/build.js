#!/usr/bin/env node

/**
 * NGX Voice Agent SDK Build Script
 * Builds all packages and creates distribution bundles
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class NGXBuilder {
    constructor() {
        this.packages = ['web', 'react', 'react-native'];
        this.buildDir = path.join(__dirname, 'dist');
        this.examplesDir = path.join(__dirname, 'examples');
    }

    async build() {
        console.log('🚀 Starting NGX Voice Agent SDK build...\n');

        try {
            // Clean previous builds
            await this.clean();

            // Install dependencies
            await this.installDependencies();

            // Build packages
            await this.buildPackages();

            // Create CDN bundles
            await this.createCDNBundles();

            // Copy examples
            await this.copyExamples();

            // Generate documentation
            await this.generateDocs();

            // Create release package
            await this.createReleasePackage();

            console.log('✅ Build completed successfully!\n');
            this.printBuildSummary();

        } catch (error) {
            console.error('❌ Build failed:', error.message);
            process.exit(1);
        }
    }

    async clean() {
        console.log('🧹 Cleaning previous builds...');
        
        if (fs.existsSync(this.buildDir)) {
            fs.rmSync(this.buildDir, { recursive: true, force: true });
        }
        
        fs.mkdirSync(this.buildDir, { recursive: true });
        
        // Clean package dist directories
        this.packages.forEach(pkg => {
            const distPath = path.join(__dirname, pkg, 'dist');
            if (fs.existsSync(distPath)) {
                fs.rmSync(distPath, { recursive: true, force: true });
            }
        });
        
        console.log('✓ Clean completed\n');
    }

    async installDependencies() {
        console.log('📦 Installing dependencies...');
        
        try {
            execSync('npm install', { cwd: __dirname, stdio: 'inherit' });
            
            // Install workspace dependencies
            this.packages.forEach(pkg => {
                const pkgDir = path.join(__dirname, pkg);
                if (fs.existsSync(path.join(pkgDir, 'package.json'))) {
                    console.log(`Installing dependencies for ${pkg}...`);
                    execSync('npm install', { cwd: pkgDir, stdio: 'inherit' });
                }
            });
            
            console.log('✓ Dependencies installed\n');
        } catch (error) {
            throw new Error(`Failed to install dependencies: ${error.message}`);
        }
    }

    async buildPackages() {
        console.log('🔨 Building packages...');
        
        for (const pkg of this.packages) {
            console.log(`Building ${pkg}...`);
            
            const pkgDir = path.join(__dirname, pkg);
            const packageJson = path.join(pkgDir, 'package.json');
            
            if (!fs.existsSync(packageJson)) {
                console.warn(`⚠️ Package.json not found for ${pkg}, skipping...`);
                continue;
            }
            
            try {
                execSync('npm run build', { cwd: pkgDir, stdio: 'inherit' });
                console.log(`✓ ${pkg} built successfully`);
            } catch (error) {
                throw new Error(`Failed to build ${pkg}: ${error.message}`);
            }
        }
        
        console.log('✓ All packages built\n');
    }

    async createCDNBundles() {
        console.log('📦 Creating CDN bundles...');
        
        const cdnDir = path.join(this.buildDir, 'cdn');
        fs.mkdirSync(cdnDir, { recursive: true });
        
        // Copy web SDK for CDN
        const webDistPath = path.join(__dirname, 'web', 'dist');
        if (fs.existsSync(webDistPath)) {
            const files = fs.readdirSync(webDistPath);
            
            files.forEach(file => {
                const srcPath = path.join(webDistPath, file);
                const destPath = path.join(cdnDir, file);
                fs.copyFileSync(srcPath, destPath);
            });
            
            // Create minified versions for CDN
            this.createMinifiedVersions(cdnDir);
        }
        
        console.log('✓ CDN bundles created\n');
    }

    createMinifiedVersions(cdnDir) {
        const files = fs.readdirSync(cdnDir);
        
        files.forEach(file => {
            if (file.endsWith('.js') && !file.includes('.min.')) {
                const filePath = path.join(cdnDir, file);
                const minFilePath = path.join(cdnDir, file.replace('.js', '.min.js'));
                
                // Simple minification (in production, use proper minifier)
                let content = fs.readFileSync(filePath, 'utf8');
                content = content
                    .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
                    .replace(/\s+/g, ' ') // Compress whitespace
                    .trim();
                
                fs.writeFileSync(minFilePath, content);
            }
        });
    }

    async copyExamples() {
        console.log('📋 Copying examples...');
        
        const examplesDistDir = path.join(this.buildDir, 'examples');
        
        if (fs.existsSync(this.examplesDir)) {
            this.copyDirectory(this.examplesDir, examplesDistDir);
            console.log('✓ Examples copied\n');
        } else {
            console.log('⚠️ Examples directory not found, skipping...\n');
        }
    }

    copyDirectory(src, dest) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        const items = fs.readdirSync(src);
        
        items.forEach(item => {
            const srcPath = path.join(src, item);
            const destPath = path.join(dest, item);
            
            if (fs.statSync(srcPath).isDirectory()) {
                this.copyDirectory(srcPath, destPath);
            } else {
                fs.copyFileSync(srcPath, destPath);
            }
        });
    }

    async generateDocs() {
        console.log('📚 Generating documentation...');
        
        const docsDir = path.join(__dirname, 'docs');
        const docsDistDir = path.join(this.buildDir, 'docs');
        
        if (fs.existsSync(docsDir)) {
            this.copyDirectory(docsDir, docsDistDir);
            
            // Generate API documentation
            this.generateAPIDocsIndex();
            
            console.log('✓ Documentation generated\n');
        } else {
            console.log('⚠️ Docs directory not found, skipping...\n');
        }
    }

    generateAPIDocsIndex() {
        const indexContent = `# NGX Voice Agent SDK - API Documentation

## Packages

- [Web SDK](./api/web-sdk.md) - Core JavaScript/TypeScript SDK
- [React Components](./api/react.md) - React components and hooks
- [React Native](./api/react-native.md) - React Native mobile SDK

## Integration Guides

- [Lead Magnet Integration](./integration/lead-magnet.md)
- [Landing Page Integration](./integration/landing-page.md)
- [Blog Widget Integration](./integration/blog-widget.md)
- [Mobile App Integration](./integration/mobile.md)

## Configuration

- [Complete Configuration Guide](./configuration.md)
- [Platform Types](./platform-types.md)
- [Events & Callbacks](./events.md)

## Examples

See the [examples directory](../examples/) for complete working examples.

---

Generated on: ${new Date().toISOString()}
Version: ${this.getVersion()}
`;

        const indexPath = path.join(this.buildDir, 'docs', 'index.md');
        fs.writeFileSync(indexPath, indexContent);
    }

    async createReleasePackage() {
        console.log('📦 Creating release package...');
        
        // Create package.json for the release
        const releasePackage = {
            name: '@ngx/voice-agent-sdk-release',
            version: this.getVersion(),
            description: 'NGX Voice Agent SDK - Complete release package',
            main: 'cdn/index.js',
            module: 'cdn/index.esm.js',
            types: 'cdn/index.d.ts',
            files: [
                'cdn/**/*',
                'examples/**/*',
                'docs/**/*',
                'README.md',
                'LICENSE'
            ],
            keywords: [
                'voice',
                'agent',
                'ai',
                'conversational',
                'sales',
                'sdk'
            ],
            author: 'NGX',
            license: 'MIT',
            repository: {
                type: 'git',
                url: 'https://github.com/ngx/voice-agent-sdk.git'
            },
            bugs: {
                url: 'https://github.com/ngx/voice-agent-sdk/issues'
            },
            homepage: 'https://docs.ngx-voice-agent.com'
        };
        
        fs.writeFileSync(
            path.join(this.buildDir, 'package.json'),
            JSON.stringify(releasePackage, null, 2)
        );
        
        // Copy README and LICENSE
        const rootFiles = ['README.md', 'LICENSE'];
        rootFiles.forEach(file => {
            const srcPath = path.join(__dirname, '..', file);
            const destPath = path.join(this.buildDir, file);
            
            if (fs.existsSync(srcPath)) {
                fs.copyFileSync(srcPath, destPath);
            }
        });
        
        console.log('✓ Release package created\n');
    }

    getVersion() {
        try {
            const packageJson = JSON.parse(
                fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8')
            );
            return packageJson.version || '1.0.0';
        } catch (error) {
            return '1.0.0';
        }
    }

    printBuildSummary() {
        const buildSize = this.getDirectorySize(this.buildDir);
        
        console.log('📊 Build Summary:');
        console.log('================');
        console.log(`Version: ${this.getVersion()}`);
        console.log(`Build Size: ${this.formatBytes(buildSize)}`);
        console.log(`Output Directory: ${this.buildDir}`);
        console.log('\n📦 Generated Packages:');
        
        this.packages.forEach(pkg => {
            const distPath = path.join(__dirname, pkg, 'dist');
            if (fs.existsSync(distPath)) {
                const size = this.getDirectorySize(distPath);
                console.log(`  ${pkg}: ${this.formatBytes(size)}`);
            }
        });
        
        console.log('\n🌐 CDN Files:');
        const cdnDir = path.join(this.buildDir, 'cdn');
        if (fs.existsSync(cdnDir)) {
            const files = fs.readdirSync(cdnDir);
            files.forEach(file => {
                const filePath = path.join(cdnDir, file);
                const stats = fs.statSync(filePath);
                if (stats.isFile()) {
                    console.log(`  ${file}: ${this.formatBytes(stats.size)}`);
                }
            });
        }
        
        console.log('\n🚀 Ready for deployment!');
        console.log('\nNext steps:');
        console.log('1. Test the examples in the dist/examples directory');
        console.log('2. Review the documentation in dist/docs');
        console.log('3. Deploy CDN files from dist/cdn');
        console.log('4. Publish packages with npm run publish:all');
    }

    getDirectorySize(dirPath) {
        let totalSize = 0;
        
        if (!fs.existsSync(dirPath)) {
            return 0;
        }
        
        const items = fs.readdirSync(dirPath);
        
        items.forEach(item => {
            const itemPath = path.join(dirPath, item);
            const stats = fs.statSync(itemPath);
            
            if (stats.isDirectory()) {
                totalSize += this.getDirectorySize(itemPath);
            } else {
                totalSize += stats.size;
            }
        });
        
        return totalSize;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Run the build
if (require.main === module) {
    const builder = new NGXBuilder();
    builder.build().catch(console.error);
}

module.exports = NGXBuilder;