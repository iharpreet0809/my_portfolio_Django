#!/usr/bin/env python
"""
Performance monitoring script for Django portfolio.
Tracks page load times and provides optimization recommendations.
"""

import time
import requests
from urllib.parse import urljoin
import json
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = {}
    
    def measure_page_load(self, path="/", iterations=3):
        """Measure page load time for a given path."""
        url = urljoin(self.base_url, path)
        times = []
        
        print(f"🔍 Testing {url}...")
        
        for i in range(iterations):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=30)
                end_time = time.time()
                
                load_time = end_time - start_time
                times.append(load_time)
                
                print(f"  Attempt {i+1}: {load_time:.2f}s (Status: {response.status_code})")
                
            except requests.RequestException as e:
                print(f"  Attempt {i+1}: Failed - {e}")
                times.append(None)
        
        valid_times = [t for t in times if t is not None]
        if valid_times:
            avg_time = sum(valid_times) / len(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
            
            self.results[path] = {
                'average': avg_time,
                'min': min_time,
                'max': max_time,
                'attempts': len(valid_times),
                'failed': len(times) - len(valid_times)
            }
            
            return avg_time
        else:
            print(f"  ❌ All attempts failed for {path}")
            return None
    
    def analyze_performance(self):
        """Analyze performance results and provide recommendations."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE ANALYSIS RESULTS")
        print("="*60)
        
        for path, metrics in self.results.items():
            avg_time = metrics['average']
            print(f"\n🌐 Path: {path}")
            print(f"   Average Load Time: {avg_time:.2f}s")
            print(f"   Range: {metrics['min']:.2f}s - {metrics['max']:.2f}s")
            print(f"   Success Rate: {metrics['attempts']}/{metrics['attempts'] + metrics['failed']}")
            
            # Performance rating
            if avg_time < 1.0:
                rating = "🟢 EXCELLENT"
            elif avg_time < 2.0:
                rating = "🟡 GOOD"
            elif avg_time < 3.0:
                rating = "🟠 NEEDS IMPROVEMENT"
            else:
                rating = "🔴 POOR"
            
            print(f"   Performance: {rating}")
    
    def generate_recommendations(self):
        """Generate performance optimization recommendations."""
        print("\n" + "="*60)
        print("💡 OPTIMIZATION RECOMMENDATIONS")
        print("="*60)
        
        home_metrics = self.results.get("/")
        if home_metrics:
            avg_time = home_metrics['average']
            
            if avg_time > 3.0:
                print("\n🚨 CRITICAL ISSUES:")
                print("   • Page load time > 3s - Users likely to abandon")
                print("   • Immediate action required on image optimization")
                print("   • Consider CDN implementation")
            
            elif avg_time > 2.0:
                print("\n⚠️  PERFORMANCE ISSUES:")
                print("   • Page load time > 2s - Room for improvement")
                print("   • Optimize large images and implement lazy loading")
                print("   • Combine CSS/JS files")
            
            elif avg_time > 1.0:
                print("\n✅ GOOD PERFORMANCE:")
                print("   • Page load time acceptable")
                print("   • Fine-tune for better user experience")
                print("   • Consider advanced optimizations")
            
            else:
                print("\n🎉 EXCELLENT PERFORMANCE:")
                print("   • Page load time < 1s - Great user experience!")
                print("   • Monitor and maintain current optimizations")
        
        print("\n📋 GENERAL RECOMMENDATIONS:")
        print("   1. Compress images (WebP format recommended)")
        print("   2. Enable lazy loading for below-fold content")
        print("   3. Minify and combine CSS/JS files")
        print("   4. Enable Gzip compression")
        print("   5. Use browser caching headers")
        print("   6. Consider implementing a CDN")
    
    def save_results(self, filename=None):
        """Save results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_results_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function to run performance tests."""
    print("🚀 PORTFOLIO PERFORMANCE MONITOR")
    print("="*60)
    
    # Initialize monitor
    monitor = PerformanceMonitor()
    
    # Test pages
    pages_to_test = [
        "/",  # Home page
    ]
    
    # Run tests
    for page in pages_to_test:
        monitor.measure_page_load(page, iterations=3)
        time.sleep(1)  # Brief pause between tests
    
    # Analyze results
    monitor.analyze_performance()
    monitor.generate_recommendations()
    
    # Save results
    monitor.save_results()

if __name__ == "__main__":
    main()