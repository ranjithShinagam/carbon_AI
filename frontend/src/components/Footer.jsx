import React from 'react';
import { Leaf, Twitter, Github, Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-deep-blue border-t border-white/10 mt-auto">
      <div className="mx-auto w-full max-w-screen-xl p-4 py-6 lg:py-8">
        <div className="md:flex md:justify-between">
          <div className="mb-6 md:mb-0">
            <a href="/" className="flex items-center group">
               <Leaf className="h-6 w-6 text-neon-green mr-2 group-hover:rotate-12 transition-transform" />
               <span className="self-center text-xl font-bold whitespace-nowrap text-white">Carbon<span className="text-neon-green">AI</span></span>
            </a>
            <p className="mt-4 text-sm text-blue-200/80 max-w-xs">
              Empowering industries with predictive carbon analytics to achieve a sustainable, net-zero future.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 sm:gap-6 sm:grid-cols-3">
            <div>
              <h2 className="mb-6 text-sm font-semibold text-white uppercase group-hover:text-neon-green">Resources</h2>
              <ul className="text-blue-200/80 font-medium">
                <li className="mb-4"><a href="#" className="hover:text-neon-green transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-neon-green transition-colors">API Reference</a></li>
              </ul>
            </div>
            <div>
              <h2 className="mb-6 text-sm font-semibold text-white uppercase">Company</h2>
              <ul className="text-blue-200/80 font-medium">
                <li className="mb-4"><a href="/about" className="hover:text-neon-green transition-colors">About Us</a></li>
                <li><a href="/pricing" className="hover:text-neon-green transition-colors">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h2 className="mb-6 text-sm font-semibold text-white uppercase">Legal</h2>
              <ul className="text-blue-200/80 font-medium">
                <li className="mb-4"><a href="#" className="hover:text-neon-green transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-neon-green transition-colors">Terms &amp; Conditions</a></li>
              </ul>
            </div>
          </div>
        </div>
        <hr className="my-6 border-white/10 sm:mx-auto lg:my-8" />
        <div className="sm:flex sm:items-center sm:justify-between">
          <span className="text-sm text-blue-200/80 sm:text-center block">© 2026 CarbonAI™. All Rights Reserved.</span>
          <div className="flex mt-4 sm:justify-center sm:mt-0 space-x-5">
            <a href="#" className="text-blue-200 hover:text-white transition-colors">
              <Twitter className="w-4 h-4" />
              <span className="sr-only">Twitter page</span>
            </a>
            <a href="#" className="text-blue-200 hover:text-white transition-colors">
              <Github className="w-4 h-4" />
              <span className="sr-only">GitHub account</span>
            </a>
            <a href="#" className="text-blue-200 hover:text-white transition-colors">
              <Linkedin className="w-4 h-4" />
              <span className="sr-only">LinkedIn account</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
