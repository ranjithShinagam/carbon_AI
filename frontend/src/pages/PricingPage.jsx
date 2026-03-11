import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';

const PricingPage = () => {
  const tiers = [
    {
      name: "Starter",
      desc: "Perfect for small facilities needing basic predictive forecasting.",
      price: "$499/mo",
      features: ["Up to 1,000 predictions/mo", "Basic Feature Importance", "Standard Email Support", "1 User License"]
    },
    {
      name: "Enterprise",
      desc: "Advanced predictive modeling for immense supply chains.",
      price: "Custom",
      featured: true,
      features: ["Unlimited Predictions", "Real-time API Access", "Dedicated Account Manager", "Unlimited Seats", "Advanced AI Scenario Simulators"]
    }
  ];

  return (
    <div className="pt-24 pb-16 min-h-screen bg-deep-blue text-soft-white max-w-7xl mx-auto px-4">
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4">Transparent Pricing for Sustainability</h1>
        <p className="text-xl text-blue-200/80">Choose the tier that fits your facility's size.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        {tiers.map((tier, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.2 }}
            className={`glass-card p-8 relative flex flex-col ${tier.featured ? 'border-neon-green/50 shadow-[0_0_30px_rgba(57,255,20,0.1)]' : ''}`}
          >
            {tier.featured && (
              <span className="absolute -top-4 left-1/2 -translate-x-1/2 bg-neon-green text-deep-blue text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                Most Popular
              </span>
            )}
            <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
            <p className="text-sm text-blue-200/70 mb-6 h-10">{tier.desc}</p>
            <div className="mb-6">
              <span className="text-4xl font-extrabold text-white">{tier.price}</span>
            </div>
            <ul className="space-y-4 flex-1 mb-8">
              {tier.features.map((feature, idx) => (
                <li key={idx} className="flex items-center text-blue-100/90">
                  <Check className="w-5 h-5 text-neon-green mr-3 flex-shrink-0" /> {feature}
                </li>
              ))}
            </ul>
            <Link 
              to="/register" 
              className={`w-full py-3 rounded-lg font-bold text-center transition-colors ${tier.featured ? 'bg-neon-green text-deep-blue hover:bg-green-400' : 'bg-white/10 hover:bg-white/20'}`}
            >
              Get Started
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default PricingPage;
